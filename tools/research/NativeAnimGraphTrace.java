// NBA11 animation graph native fixups and motion binding. Synthetic memory only.
// Args: NEW_OUTPUT_JSON. No asset or executable mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
public class NativeAnimGraphTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,long value){e.writeMemoryValue(toAddr(at),4,value);}
 private String trace(int count,boolean grouped) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long base=0x40004000L,table=0x40008000L,header=0x40009000L,group=0x4000a000L,done=0x4000f000L;
   byte[] initial=new byte[0x2000];Arrays.fill(initial,(byte)0x5a);e.writeMemory(toAddr(base),initial);
   Map<Integer,Long> changes=new TreeMap<>();int next=128;
   int[] strides={36,24,4,8,12,4,16,16,16,16,16,16,16,16,16,16};
   int[] counts=new int[16];Arrays.fill(counts,1);counts[0]=count;int[] offsets=new int[16];
   for(int i=0;i<16;i++){
    offsets[i]=next;word(e,base+i*4,counts[i]);word(e,base+64+i*4,next-(64+i*4)+1);
    changes.put(64+i*4,base+next);next+=counts[i]*strides[i];
   }
   // Every native pointer class gets a valid non-null and/or null representative.
   for(int i=0;i<16;i++)for(int n=0;n<counts[i];n++){
    int row=offsets[i]+n*strides[i];int[] fields;
    if(i==0){word(e,base+row+16,grouped&&n==0?1:0);fields=new int[]{24,32};}
    else if(i==1)fields=new int[]{12,20};
    else if(i==2)fields=new int[]{};
    else if(i==3)fields=new int[]{4};
    else if(i<7)fields=new int[]{0};
    else fields=new int[]{4,8,12};
    for(int f:fields){int at=row+f;boolean nullPointer=(f==32||f==20||f==8);long target=base+0x1800;
     word(e,base+at,nullPointer?0:target-(base+at)+1);changes.put(at,nullPointer?0:target);
    }
   }
   for(int n=0;n<count;n++){
    long target=header+n*64;word(e,table+n*4,grouped&&n==0?group:target);
    int row=offsets[0]+n*36;
    if(grouped&&n==0){word(e,group+12,target);changes.put(row,group);}
    changes.put(row+4,target);
   }
   byte[] before=e.readMemory(toAddr(base),initial.length);byte[] expected=before.clone();
   for(Map.Entry<Integer,Long> change:changes.entrySet())ByteBuffer.wrap(expected).putInt(change.getKey(),change.getValue().intValue());
   e.writeMemory(toAddr(0x40000000L),new byte[0x2000]);
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);e.writeRegister("r3",base);e.writeRegister("r4",table);
   e.writeRegister("LR",done);e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x37fc60L);
   boolean complete=false;int steps=0;
   for(;steps<8192;steps++){
    long pc=e.getExecutionAddress().getOffset();if(pc==done){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Graph instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete)throw new Exception("Graph instruction bound exceeded");
   if(!Arrays.equals(expected,e.readMemory(toAddr(base),initial.length)))throw new Exception("Graph pointer binding or untouched bytes mismatch");
   return "{\"nodes\":"+count+",\"grouped_node\":"+grouped+",\"steps\":"+steps+",\"passed\":true}";
  }finally{e.dispose();}
 }
 private String lookup(int family,String mode) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long base=0x40004000L,table=base+0x800,done=0x4000f000L,key=0xffffffffL;
   e.writeMemory(toAddr(base),new byte[0x1000]);word(e,0x4b93d2cL,base);
   word(e,base+0x1c+4*family,mode.equals("empty")?0:2);
   word(e,base+0x5c+4*family,table);
   word(e,table,key);word(e,table+16,mode.equals("duplicate")?key:0x12345678);
   long query=mode.equals("last")?0x12345678:mode.equals("missing")?7:key;
   long expected=mode.equals("empty")||mode.equals("missing")?0:table+(mode.equals("last")?16:0);
   byte[] before=e.readMemory(toAddr(base),0x1000);
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("xer_so",0);e.writeRegister("r3",query);e.writeRegister("r4",family);e.writeRegister("LR",done);
   e.writeRegister(e.getPCRegister(),0x4691f8L);boolean complete=false;
   for(int step=0;step<256;step++){
    long pc=e.getExecutionAddress().getOffset();if(pc==done){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Lookup instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete||e.readRegister("r3").longValue()!=expected)throw new Exception("Native graph lookup mismatch");
   if(!Arrays.equals(before,e.readMemory(toAddr(base),0x1000)))throw new Exception("Graph lookup changed storage");
   return "{\"kind\":\"lookup\",\"family\":"+family+",\"mode\":\""+mode+"\",\"passed\":true}";
  }finally{e.dispose();}
 }
 private String playerRouting(String mode) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long base=0x40004000L,actor=0x40002000L,player=0x40003000L,state=0x40006000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);word(e,0x4b93d2cL,base);word(e,actor+0x64,player);
   byte[] before=new byte[0x100];Arrays.fill(before,(byte)0x5a);e.writeMemory(toAddr(state),before);byte[] expected=before.clone();
   int[] fields={0x100,0x108,0x110,0x10c,0x104,0x11c,0x114,0x118,0x120};
   for(int f=0;f<9;f++){
    long table=base+0x800+32*f,first=0x80000000L+f,last=0xf0000000L+f;
    word(e,base+0x1c+4*f,2);word(e,base+0x5c+4*f,table);word(e,table,first);word(e,table+16,last);
    word(e,player+fields[f],mode.equals("first")?first:mode.equals("last")?last:7+f);
    ByteBuffer.wrap(expected).putInt(0x4c+4*f,mode.equals("missing")?0:(int)table+(mode.equals("last")?16:0));
   }
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("r27",state);e.writeRegister("r28",actor);e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x46d07cL);
   boolean complete=false;
   for(int step=0;step<2048;step++){
    long pc=e.getExecutionAddress().getOffset();if(pc==0x46d110L){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Player routing failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete||!Arrays.equals(expected,e.readMemory(toAddr(state),before.length)))throw new Exception("Player graph family/cache routing mismatch");
   return "{\"kind\":\"player-routing\",\"mode\":\""+mode+"\",\"passed\":true}";
  }finally{e.dispose();}
 }
 private String reset(int seed) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long actor=0x40002000L,data=0x40003000L,parameters=0x40004000L,state=data+0x110;
   e.writeMemory(toAddr(0x40000000L),new byte[0x6000]);word(e,actor+0x14,data);word(e,actor+0x10,parameters);
   word(e,parameters+0x18,seed);word(e,parameters+0x14,Float.floatToRawIntBits(1.25f));
   byte[] before=new byte[0x100];Arrays.fill(before,(byte)0x5a);e.writeMemory(toAddr(state),before);
   byte[] expected=before.clone();Arrays.fill(expected,0,0x70,(byte)0);ByteBuffer.wrap(expected).putInt(0x30,seed);ByteBuffer.wrap(expected).putInt(0x2c,Float.floatToRawIntBits(1.25f));
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("r26",actor);e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x46cb4cL);boolean complete=false;
   for(int step=0;step<512;step++){
    long pc=e.getExecutionAddress().getOffset();if(pc==0x46cb6cL){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Cache reset failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete||e.readRegister("r27").longValue()!=state||!Arrays.equals(expected,e.readMemory(toAddr(state),before.length)))throw new Exception("Cache reset/state address mismatch");
   return "{\"kind\":\"cache-reset\",\"seed\":"+seed+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=1)throw new Exception("Supply NEW output path");
  Path out=Paths.get(args[0]);if(Files.exists(out))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x37fcd0))!=0x2f800000||getInt(toAddr(0x37fd2c))!=0x3bde0024||getInt(toAddr(0x8339ac))!=0x80030000||getInt(toAddr(0x4691f8))!=0x3d2004b9||getInt(toAddr(0x46d07c))!=0x83bc0064||getInt(toAddr(0x469774))!=0x38040070)
   throw new Exception("Unsupported native graph revision");
  List<String> rows=new ArrayList<>();rows.add(trace(0,false));rows.add(trace(1,false));rows.add(trace(2,true));
  for(int family=0;family<9;family++)for(String mode:new String[]{"first","last","missing","empty","duplicate"})rows.add(lookup(family,mode));
  for(String mode:new String[]{"first","last","missing"})rows.add(playerRouting(mode));
  rows.add(reset(0));rows.add(reset(0x12345678));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native animation graph fixups/lookups: "+rows.size()+" cases passed");
 }
}
