// Native paired-rate adjustment in both games; synthetic headers only.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeMotionRateTrace extends GhidraScript {
 private boolean donor;
 private void word(EmulatorHelper e,long at,long value){e.writeMemoryValue(toAddr(at),4,value);}
 private String trace(int[] divisors,float[] input,float weight,int flags) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long first=0x40002000L,second=0x40002100L,out=0x40003000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   for(int i=0;i<2;i++){long h=first+256*i;word(e,h+0x10,0x3c000002L);word(e,h+0x14,0xd0000003L|((long)divisors[i]<<24));word(e,h+0x18,(flags&(1<<i))!=0?0x10:0);word(e,h+0x20,Float.floatToRawIntBits(input[i]));}
   byte[] headers=e.readMemory(toAddr(first),0x200),sent=new byte[32];Arrays.fill(sent,(byte)0x5a);e.writeMemory(toAddr(out),sent);
   for(int i=0;i<32;i++){e.writeRegister("r"+i,0);e.writeRegister("f"+i,0);}for(var r:currentProgram.getLanguage().getRegisters())if(r.getName().startsWith("fp_")||r.getName().toLowerCase().contains("fpscr"))e.writeRegister(r.getName(),0);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",donor?0x40f2a98L:0xa54ac8L);e.writeRegister("r3",first);e.writeRegister("r4",second);e.writeRegister("r8",out+8);e.writeRegister("r9",out+16);e.writeRegister("xer_so",0);e.writeRegister("LR",0x4000f000L);
   e.writeRegister("f1",Double.doubleToRawLongBits(input[2]));e.writeRegister("f2",Double.doubleToRawLongBits(input[3]));e.writeRegister("f3",Double.doubleToRawLongBits(weight));e.writeRegister(e.getPCRegister(),donor?0x119dcL:0x24f94L);
   boolean done=false;for(int step=0;step<256;step++){if(e.getExecutionAddress().getOffset()==0x4000f000L){done=true;break;}if(!e.step(monitor))throw new Exception("Rate instruction failure: "+e.getLastError());}
   float a=input[2],b=input[3];if(flags==0){float da=input[0]/Math.max(1,divisors[0]),db=input[1]/Math.max(1,divisors[1]),one=1.0f-weight;a=Math.fma(input[2],one,((da*input[3])/db)*weight);b=Math.fma(input[3],weight,((db*input[2])/da)*one);}
   byte[] expected=sent.clone();java.nio.ByteBuffer bb=java.nio.ByteBuffer.wrap(expected);bb.putInt(8,Float.floatToRawIntBits(a));bb.putInt(16,Float.floatToRawIntBits(b));
   if(!done||!Arrays.equals(headers,e.readMemory(toAddr(first),headers.length))||!Arrays.equals(expected,e.readMemory(toAddr(out),32)))throw new Exception("Native rate result/header/sentinel mismatch: "+Arrays.toString(divisors)+" "+weight+" "+flags);
   return "{\"divisors\":"+Arrays.toString(divisors)+",\"weight\":"+weight+",\"flags\":"+flags+",\"rate_bits\":["+Integer.toUnsignedLong(Float.floatToRawIntBits(a))+","+Integer.toUnsignedLong(Float.floatToRawIntBits(b))+"],\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] a=getScriptArgs();if(a.length!=2)throw new Exception("Supply profile and NEW JSON");donor=a[0].equals("nba-2k11");if(!donor&&!a[0].equals("college-hoops-2k8"))throw new Exception("Bad profile");Path out=Paths.get(a[1]);if(Files.exists(out))throw new Exception("Existing output refused");if(getInt(toAddr(donor?0x119dc:0x24f94))!=0x80030018)throw new Exception("Unsupported rate revision");
  List<String> rows=new ArrayList<>();for(int[] d:new int[][]{{0,0},{1,0},{0,3},{3,1},{15,3}})for(float[] input:new float[][]{{1,2,1,2},{2.4f,.7f,-1,.75f},{.5f,3.1f,1.3f,.4f},{5,5,0,1}})for(float w:new float[]{-.25f,0,.25f,.5f,1,1.25f,.3f})for(int flags=0;flags<4;flags++)rows.add(trace(d,input,w,flags));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]",StandardOpenOption.CREATE_NEW);println("Native motion rates "+a[0]+": "+rows.size()+" passed");
 }
}
