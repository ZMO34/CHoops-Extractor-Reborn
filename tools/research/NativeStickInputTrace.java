// Revision-guarded NBA2K14 PS3 input-prefix instruction harness.
// Synthetic CellPadData only. No game, RPCS3, executable patch or JB runs.
// Argument: a NEW output JSON path. Stops after axes, before later input logic.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

public class NativeStickInputTrace extends GhidraScript {
 private void word(EmulatorHelper e,long a,int value){e.writeMemoryValue(toAddr(a),4,value);}
 private int readWord(EmulatorHelper e,long a){return ByteBuffer.wrap(e.readMemory(toAddr(a),4)).getInt();}
 private void revision() throws Exception {
  long[] at={0xb5daf0L,0xb5dc94L,0xb5dcc0L,0xb5dcecL,0xb5dd04L,0xb5dad8L,0xb5dadcL,0xb5dae0L};
  int[] expected={0x7c0802a6,0xd07f0110,0xd07f0120,0xd07f0130,0xd07f0140,0x40000000,0x3b808081,0x3f800000};
  for(int i=0;i<at.length;i++)if(getInt(toAddr(at[i]))!=expected[i])throw new Exception("Unsupported NBA14 input revision at "+Long.toHexString(at[i]));
 }
 private String runCase(int port,int[] axes,int length,int packetType,int apiResult) throws Exception {
  if(port<0||port>6)throw new Exception("CellPad port outside 0..6");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long record=0x1457fe8L+port*0x310L,stack=0x40001000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x8000]);
   word(e,0x1459560L,0);word(e,record+8,2);word(e,record+12,0);
   for(int offset:new int[]{0x110,0x120,0x130,0x140})word(e,record+offset,0x12345678);
   e.writeRegister("r1",stack);e.writeRegister("r2",0xe4dad0L);e.writeRegister("r3",0);e.writeRegister("r4",0);e.writeRegister("r5",0);e.writeRegister("xer_so",0);
   e.writeRegister("LR",0x40007000L);e.writeRegister(e.getPCRegister(),0xb5daf0L);
   boolean valid=apiResult==0&&length>=8&&(packetType&0xf0)==0x70&&(packetType&15)>=4;
   boolean requested=false;List<Integer> bits=new ArrayList<>(); List<String> recent=new ArrayList<>();
   for(int step=0;step<256;step++){
    long pc=e.getExecutionAddress().getOffset(); recent.add(Long.toHexString(pc)); if(recent.size()>12)recent.remove(0);
    if(pc==0xc36efcL){e.writeRegister("r3",port);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
    if(pc==0xcd4798L){
     if(e.readRegister("r3").intValue()!=port)throw new Exception("CellPad port argument mismatch");
     long packet=e.readRegister("r4").longValue();e.writeMemory(toAddr(packet),new byte[132]);word(e,packet,length);
     e.writeMemoryValue(toAddr(packet+6),2,packetType);
     // CellPad button[4..7]: right X/Y, left X/Y, per the native ABI.
     for(int i=0;i<4;i++)e.writeMemoryValue(toAddr(packet+12+i*2),2,axes[i]);
     requested=true;e.writeRegister("r3",apiResult);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;
    }
    if(pc==(valid?0xb5dd08L:0xb5e0a8L)){
     if(!requested)throw new Exception("CellPad request not observed");
     int[] axisOrder={2,3,0,1};
     for(int i=0;i<4;i++){
      int actual=readWord(e,record+0x110+i*16);
      float value=Math.fma((float)(axes[axisOrder[i]]*2),Float.intBitsToFloat(0x3b808081),-1.0f);
      if((i&1)!=0)value=-value;
      int expected=valid?Float.floatToRawIntBits(value):0x12345678;
      if(actual!=expected)throw new Exception("Axis bits mismatch port "+port+" axis "+i+" actual "+Integer.toHexString(actual)+" expected "+Integer.toHexString(expected));
      bits.add(actual);
     }
     return "{\"port\":"+port+",\"packet_axes_right_then_left\":"+Arrays.toString(axes)+",\"valid\":"+valid+",\"axis_bits_left_then_right\":"+bits+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+" recent "+recent+": "+e.getLastError());
   }
   throw new Exception("NBA14 input prefix exceeded instruction bound");
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  revision();
  Path output=Paths.get(getScriptArgs()[0]).toAbsolutePath().normalize();
  if(Files.exists(output))throw new Exception("Choose a new output path; no source/report overwrite");
  List<String> rows=new ArrayList<>();
  int[] samples={0,1,127,128,254,255};
  for(int i=0;i<samples.length;i++)rows.add(runCase(i%2==0?0:6,new int[]{samples[i],samples[5-i],samples[(i+2)%6],samples[(i+3)%6]},8,0x74,0));
  rows.add(runCase(0,new int[]{0,255,0,255},7,0x74,0));
  rows.add(runCase(6,new int[]{0,255,0,255},8,0x44,0));
  rows.add(runCase(0,new int[]{0,255,0,255},8,0x74,1));
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("NBA2K14 input-prefix native instruction cases: "+rows.size()+" passed");
 }
}
