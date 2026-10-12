"""ATRAC3 decoding and encoding with open-source codec components."""
import io
import math
import os
import shutil
import struct
import subprocess
import time
import uuid
import wave
from pathlib import Path
from ..archive.manifests import OUTPUT

FRAME_SAMPLES=1024
BYTES_PER_CHANNEL=152
GAME_DELAY=2048
ENCODER_DELAY=1162


def decoder_module():
    try:
        import av
    except ImportError as error:
        raise ValueError('Audio decoding needs PyAV; run audio commands from the Python audio-workspace after tools/dev/setup.py') from error
    return av


def atrac_riff(data,channels,rate):
    if channels not in (1,2) or not 8000<=rate<=192000:raise ValueError('Unsupported ATRAC3 channel/rate configuration')
    align=BYTES_PER_CHANNEL*channels
    if not data or len(data)%align:raise ValueError('ATRAC3 stream ends inside a frame')
    extra=struct.pack('<HIHHHH',1,1024,0,0,1,0)
    fmt=struct.pack('<HHIIHHH',0x270,channels,rate,align*rate//1024,align,0,14)+extra
    body=b'WAVEfmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(data))+data
    return b'RIFF'+struct.pack('<I',len(body))+body


def export_wav(data,channels,rate,output,samples=None,job=None):
    av=decoder_module()
    converter=av.AudioResampler(format='s16',layout='mono' if channels==1 else 'stereo',rate=rate)
    skip=GAME_DELAY;written=0
    with av.open(io.BytesIO(atrac_riff(data,channels,rate))) as source,wave.open(str(output),'wb') as target:
        target.setnchannels(channels);target.setsampwidth(2);target.setframerate(rate)
        for frame in source.decode(audio=0):
            if job:job.check()
            for pcm in converter.resample(frame):
                start=min(skip,pcm.samples);skip-=start;count=pcm.samples-start
                if samples is not None:count=min(count,max(0,samples-written))
                target.writeframesraw(bytes(pcm.planes[0])[start*channels*2:(start+count)*channels*2]);written+=count
        if samples is not None and written!=samples:raise ValueError('Decoded audio is shorter than its declared sample range')
    if not written:raise ValueError('Audio stream has no samples after decoder priming')
    return dict(channels=channels,sample_rate=rate,samples=written,seconds=written/rate,format='PCM16 WAV')


def encoder_path():
    path=Path(__file__).parent/'bin'/('choops_atrac3_encoder.exe' if os.name=='nt' else 'choops_atrac3_encoder')
    if not path.is_file():raise ValueError('ATRAC encoder is missing; build it with tools/audio_encoder/build.py or use the Windows release')
    return path


def encode_wav(source,channels,rate,job=None):
    if channels not in (1,2) or not 8000<=rate<=192000:raise ValueError('Unsupported ATRAC3 channel/rate configuration')
    av=decoder_module()
    work=OUTPUT/'temp'/('audio_encode_'+uuid.uuid4().hex);work.mkdir(parents=True)
    pcm_path=work/'input.f32';encoded=work/'output.at3';samples=0
    try:
        converter=av.AudioResampler(format='flt',layout='mono' if channels==1 else 'stereo',rate=rate)
        with av.open(str(Path(source).resolve())) as media,pcm_path.open('wb') as pcm:
            if media.format.name!='wav' or len(media.streams.audio)!=1:raise ValueError('Choose one WAV audio stream')
            pcm.write(b'\0'*((GAME_DELAY-ENCODER_DELAY)*channels*4))
            for frame in media.decode(audio=0):
                if job:job.check()
                for output in converter.resample(frame):
                    pcm.write(bytes(output.planes[0])[:output.samples*channels*4]);samples+=output.samples
                    if samples>rate*1800:raise ValueError('A replacement track may not exceed 30 minutes')
            for output in converter.resample(None):
                pcm.write(bytes(output.planes[0])[:output.samples*channels*4]);samples+=output.samples
        if not samples:raise ValueError('WAV contains no audio samples')
        if job:job.progress(0,1,'Encoding ATRAC3 replacement');job.check()
        with (work/'encoder.log').open('wb') as log:
            process=subprocess.Popen([str(encoder_path()),str(pcm_path),str(encoded),str(channels)],stdout=log,stderr=log,
                                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                deadline=time.monotonic()+1800
                while process.poll() is None:
                    if job:job.check()
                    if time.monotonic()>deadline:raise ValueError('ATRAC encoding timed out')
                    time.sleep(.1)
            finally:
                if process.poll() is None:process.kill();process.wait()
        if process.returncode:raise ValueError('ATRAC encoder failed: '+(work/'encoder.log').read_text(errors='replace')[-500:])
        data=encoded.read_bytes();align=BYTES_PER_CHANNEL*channels
        if len(data)%align or len(data)//align*1024-GAME_DELAY<samples:raise ValueError('Encoded replacement has an invalid sample extent')
        export_wav(data,channels,rate,work/'validated.wav',samples,job)
        return data,samples
    finally:
        if work.resolve().is_relative_to((OUTPUT/'temp').resolve()):shutil.rmtree(work)


def playback_samples(encoded_size,channels,rate,stored=None):
    align=BYTES_PER_CHANNEL*channels
    if not encoded_size or encoded_size%align:raise ValueError('Audio byte count is not frame-aligned')
    physical=encoded_size//align*1024-GAME_DELAY
    if physical<=0:raise ValueError('Audio stream is too short')
    if stored is not None and math.isfinite(stored):
        target=round(stored)
        if 0<target<=physical and physical-target<=8192:return target
    return physical
