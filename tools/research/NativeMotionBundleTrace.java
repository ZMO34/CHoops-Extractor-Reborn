// CH bundle selection prefix only; stop before timing/playback functions.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeMotionBundleTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,long v){e.writeMemoryValue(toAddr(at),4,v);}
 private String trace(int count,int valueIndex,boolean allow,boolean policy,boolean flag,int guard) throws Exception {
  float[] values={-.1f,0,.4f,.8f,.9f,1};float[] thresholds={0,.4f,.625f,.9f,.9f};
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long actor=0x40002000L,data=0x40003000L,bundle=0x40005000L,perActor=0x40008000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x20000]);word(e,actor+0x14,data);word(e,actor+0x70,2);
   e.writeMemoryValue(toAddr(data+0xf0),8,flag?2:0);word(e,0xa58f6cL,perActor);word(e,perActor+2*416+0x108,Float.floatToRawIntBits(values[valueIndex]));
   for(int i=0;i<count;i++){
    word(e,bundle+24*i,0x50000000L+0x100*i);word(e,bundle+24*i+4,0x50000040L+0x100*i);
    word(e,bundle+24*i+8,Float.floatToRawIntBits(thresholds[i]));word(e,bundle+24*i+12,Float.floatToRawIntBits(1.0f+i*.125f));word(e,bundle+24*i+16,Float.floatToRawIntBits(2.0f+i*.125f));word(e,bundle+24*i+20,i==count-1?1:0);
   }
   word(e,bundle+24*count+20,guard);
   for(int i=0;i<32;i++){e.writeRegister("r"+i,0);e.writeRegister("f"+i,0);}
   for(var r:currentProgram.getLanguage().getRegisters())if(r.getName().startsWith("fp_")||r.getName().toLowerCase().contains("fpscr"))e.writeRegister(r.getName(),0);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0xa54ac8L);e.writeRegister("r3",actor);e.writeRegister("r4",bundle);e.writeRegister("r5",allow?1:0);e.writeRegister("r6",policy?1:0);e.writeRegister("r8",count);e.writeRegister("xer_so",0);e.writeRegister("LR",0);e.writeRegister(e.getPCRegister(),0x345abcL);
   byte[] original=e.readMemory(toAddr(bundle),24*(count+1));long lookahead=-1;
   boolean done=false;
   for(int step=0;step<512;step++){
    long pc=e.getExecutionAddress().getOffset();if(pc==0x345fdcL)lookahead=e.readRegister("r9").longValue()+0x2c;if(pc==0x345bd8L){done=true;break;}
    if(!e.step(monitor))throw new Exception("Bundle instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   int selected=-1;for(int i=count-1;i>=0;i--)if(thresholds[i]<=values[valueIndex]&&(allow||i!=count-1)){selected=i;break;}
   int lane=policy&&!flag?1:0,next=selected;
   if(selected>=0){int following=selected+1<count?(selected+1==count-1?1:0):guard;next=Math.min(count-1,selected+((allow||(following&1)==0)?1:0));}
   long first=selected<0?0:0x50000000L+256*selected+64*lane,second=selected<0?0:0x50000000L+256*next+64*lane;
   if(lookahead!=(selected<0?-1:bundle+24*(selected+1)+20)||!Arrays.equals(original,e.readMemory(toAddr(bundle),original.length)))throw new Exception("Lookahead address or bundle preservation mismatch");
   double scalar=selected<0?1.0:(lane==0?1.0:2.0)+selected*.125;
   if(!done||e.readRegister("r31").intValue()!=selected||e.readRegister("r27").longValue()!=first||e.readRegister("r25").longValue()!=second||Double.longBitsToDouble(e.readRegister("f30").longValue())!=scalar||Double.longBitsToDouble(e.readRegister("f31").longValue())!=scalar)throw new Exception("Bundle selection mismatch");
   return "{\"count\":"+count+",\"value_index\":"+valueIndex+",\"allow\":"+allow+",\"policy\":"+policy+",\"flag\":"+flag+",\"guard\":"+guard+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] a=getScriptArgs();if(a.length!=1)throw new Exception("Supply NEW JSON");Path out=Paths.get(a[0]);if(Files.exists(out))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x345b18))!=0x80e244a4||getInt(toAddr(0x345fdc))!=0x8009002c)throw new Exception("Unsupported bundle revision");
  List<String> rows=new ArrayList<>();for(int count:new int[]{1,5})for(int v=0;v<6;v++)for(boolean allow:new boolean[]{false,true})for(boolean policy:new boolean[]{false,true})for(boolean flag:new boolean[]{false,true})for(int guard:new int[]{0,1})rows.add(trace(count,v,allow,policy,flag,guard));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]",StandardOpenOption.CREATE_NEW);println("Native motion bundle prefix: "+rows.size()+" passed");
 }
}
