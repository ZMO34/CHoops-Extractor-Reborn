// Bounded NBA11 cache fallback graph. Synthetic pointers/pools; no game writes.
// Args: NEW_OUTPUT_JSON. Random/context service calls are explicit test inputs.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

public class NativeShotFallbackTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,int v){e.writeMemoryValue(toAddr(at),4,v);}
 private int read(EmulatorHelper e,long at){return ByteBuffer.wrap(e.readMemory(toAddr(at),4)).getInt();}
 private String trace(int bit,int mask,int bucket,int mode,double random) throws Exception {
  if(getInt(toAddr(0x6536c8))!=0x911f001c ||getInt(toAddr(0x6536dc))!=0x913f0020
    ||getInt(toAddr(0x6538c0))!=0x4bfffe78)
   throw new Exception("Unsupported NBA11 fallback revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long cache=0x40002000L,player=0x40003000L,ctx=0x40004000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   for(int p=0;p<4;p++)word(e,cache+8+p*4,(mask&(1<<p))!=0?0x50000000+p*0x100:0);
   e.writeMemoryValue(toAddr(player+0x1c),2,bucket);
   word(e,ctx+0x10,0x40005000);word(e,0x40005000,mode==0?-1:17);
   for(int row=0;row<18;row++){
    long at=0x434f270L+row*32;
    word(e,at+4,0x51000000+row*0x100);word(e,at+12,0x52000000+row*0x100);
    word(e,at+20,0x53000000+row*0x100);word(e,at+28,0x54000000+row*0x100);
   }
   for(int row=0;row<8;row++){
    long at=0x434f1d0L+row*20;
    word(e,at+4,0x55000000+row*0x100);word(e,at+12,0x56000000+row*0x100);
    word(e,at+16,Float.floatToRawIntBits(1));
   }
   word(e,0xa51564L,123);
   word(e,0x434f1c4L,0x57000000);word(e,0x434f1ccL,0x58000000);
   for(String reg:new String[]{"fp_xx","fp_fi","fp_vxsnan","fp_vxisi","fp_vxidi","fp_vxzdz","fp_vximz","fp_vxvc","fp_vxsoft","fp_vxsqrt","fp_vxcvi","fp_fx","fp_ox","fp_ux","fp_zx","fp_ve","fp_oe","fp_ue","fp_ze","fp_xe"})e.writeRegister(reg,0);
   e.writeRegister("xer_so",0);e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);
   e.writeRegister("r31",cache);e.writeRegister("r26",player);e.writeRegister("r30",bit);
   e.writeRegister("r24",mode<0?0:ctx);e.writeRegister("r25",ctx);
   e.writeRegister(e.getPCRegister(),0x653644L);
   int draws=0,contextCalls=0,generatorCalls=0;
   for(int step=0;step<1024;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==0x653648L){
     e.writeRegister("r9",0);e.writeRegister("r11",0xa50000L);
     e.writeRegister("r10",read(e,cache+8));e.writeRegister(e.getPCRegister(),0x65369cL);continue;
    }
    if(pc==0x871b30L){generatorCalls++;e.writeRegister("r3",0x40006000L);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
    if(pc==0x871cf8L){draws++;e.writeRegister("f1",Double.doubleToRawLongBits(random));e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
    if(pc==0x1203f4L){contextCalls++;e.writeRegister("r3",mode==2?1:0);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
    if(pc==0x6537b0L){
     int[] expected=new int[4];
     for(int p=0;p<4;p++)expected[p]=(mask&(1<<p))!=0?0x50000000+p*0x100:0;
     if(expected[0]==0){int row=random==0?7:random==0.25?2:0;expected[0]=(bit==1?0x55000000:0x56000000)+row*0x100;}
     if(expected[1]==0){expected[1]=(bit==1?0x51000000:0x52000000)+(bucket%18)*0x100;expected[2]=(bit==1?0x53000000:0x54000000)+(bucket%18)*0x100;}
     if(expected[2]==0)expected[2]=bit==1?0x3f8c798:0x3f8c7d0;
     if(expected[3]==0||mode==2)expected[3]=bit==1?0x57000000:0x58000000;
     for(int p=0;p<4;p++)if(read(e,cache+8+p*4)!=expected[p])throw new Exception("Fallback mismatch pair "+p);
     if(read(e,cache+0x1c)!=((mask&1)!=0?1:0)||read(e,cache+0x20)!=((mask&2)!=0?1:0))throw new Exception("Presence flags were replaced by fallback availability");
     if(read(e,cache+0x18)!=(((mask&8)==0||mode==2)?0:123))throw new Exception("Control value reset mismatch");
     if(draws!=((mask&1)!=0?0:8)||contextCalls!=(mode>=1?1:0)||generatorCalls!=draws+((mask&8)==0||mode==2?1:0))throw new Exception("Unexpected service calls");
     return "{\"selector_bit\":"+bit+",\"mask\":"+mask+",\"bucket\":"+bucket+",\"context\":"+(mode==2)+",\"random\":"+random+",\"context_mode\":"+mode+",\"draws\":"+draws+",\"motions\":"+Arrays.toString(expected)+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   throw new Exception("Fallback graph exceeded instruction bound");
  } finally {e.dispose();}
 }
 private String cacheKey(int variant) throws Exception {
  if(getInt(toAddr(0x6533cc))!=0x800b0000)throw new Exception("Unsupported native cache-key revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long player=0x40003000L,cache=0x4c5a588L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   word(e,cache,variant==0?0:variant==1?(int)player+0x100:(int)player);
   word(e,cache+4,variant==3?18:17);word(e,player+0xd4,17);
   word(e,player+0xcc,variant==4?1:0);
   e.writeRegister("xer_so",0);e.writeRegister("r3",player);e.writeRegister("LR",0x40007000L);
   e.writeRegister(e.getPCRegister(),0x6533c0L);
   for(int step=0;step<32;step++){
    if(e.getExecutionAddress().getOffset()==0x40007000L){
     int expected=variant==2||variant==4?1:0;
     if(e.readRegister("r3").intValue()!=expected)throw new Exception("Native cache key mismatch");
     return "{\"cache_variant\":"+variant+",\"hit\":"+(expected==1)+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Cache-key instruction failure");
   }
   throw new Exception("Cache-key instruction bound exceeded");
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=1)throw new Exception("Supply NEW JSON path");
  Path output=Paths.get(args[0]).toAbsolutePath().normalize();
  if(Files.exists(output))throw new Exception("Existing source/report overwrite refused");
  List<String> rows=new ArrayList<>();
  for(int bit=0;bit<2;bit++)for(int mask=0;mask<16;mask++)for(int mode=-1;mode<=2;mode++)
   rows.add(trace(bit,mask,65535,mode,0.25));
  for(int bit=0;bit<2;bit++)for(int bucket:new int[]{0,17,18})for(double random:new double[]{0,0.99})
   rows.add(trace(bit,0,bucket,-1,random));
  for(int variant=0;variant<5;variant++)rows.add(cacheKey(variant));
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native shot fallback graph: "+rows.size()+" cases passed");
 }
}
