// NBA11 native group relocation and member alias-copy loops. Synthetic memory only.
// Args: NEW_OUTPUT_JSON. Asset/executable inputs remain read-only.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
public class NativeMotionGroupTrace extends GhidraScript {
 private void word(EmulatorHelper e,long a,long v){e.writeMemoryValue(toAddr(a),4,v);}
 private long read(EmulatorHelper e,long a){return Integer.toUnsignedLong(ByteBuffer.wrap(e.readMemory(toAddr(a),4)).getInt());}
 private String trace(int count,boolean alias) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long group=0x40002000L,owner=0x40003000L,done=0x4000f000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);word(e,group+8,count);word(e,owner+8,count);
   for(int i=0;i<count;i++){
    long h=0x40004000L+i*0x200L,p=0x40006000L+i*0x200L,field=group+12+i*16;
    word(e,field,alias?h:h-field+1);word(e,owner+12+i*16,p);
    for(int j=1;j<4;j++)word(e,field+j*4,0x12340000+i*16+j);
    word(e,h,0x11110000+i);word(e,h+0x10,2);word(e,h+0x14,0x40000003);word(e,h+0x18,0xabcdef00+i);
    word(e,p+0x10,2);word(e,p+0x18,0x33330000+i);
    for(int f:new int[]{0x24,0x28,0x2c,0x30,0x34,0x38,0x3c}){
     long target=(alias?p:h)+0x100+f;
     word(e,alias?p+f:h+f,alias?target:target-(h+f)+1);
    }
    word(e,h+0x130,0x80000000L);
    if(alias){word(e,h+0x28,i==0?0x99990000L:0);word(e,h+0x30,0);}
   }
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);e.writeRegister("LR",done);
   e.writeRegister("xer_so",0);e.writeRegister("r29",0);e.writeRegister("r30",0);e.writeRegister("r31",0);
   if(alias){e.writeRegister("r26",owner);e.writeRegister("r27",owner);e.writeRegister("r28",group);e.writeRegister(e.getPCRegister(),0x1c7e0L);}
   else{e.writeRegister("r3",group);e.writeRegister(e.getPCRegister(),0x1602cL);}
   boolean complete=false;
   for(int step=0;step<4096;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==(alias?0x1c83cL:done)){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete)throw new Exception("Group instruction bound exceeded");
   for(int i=0;i<count;i++){
    long h=0x40004000L+i*0x200L,p=0x40006000L+i*0x200L,field=group+12+i*16;
    if(read(e,field)!=h||read(e,h)!=0x11110000L+i||read(e,h+0x18)!=0xabcdef00L+i||read(e,h+0x14)!=0x40000003L)
     throw new Exception("Original member metadata not retained");
    for(int j=1;j<4;j++)if(read(e,field+j*4)!=0x12340000+i*16+j)throw new Exception("Placement words changed");
    for(int f:new int[]{0x24,0x28,0x2c,0x30,0x34,0x38,0x3c})
     if(read(e,h+f)!=(alias?p:h)+0x100+f)throw new Exception("Member dependency mismatch");
    if(alias&&(read(e,h+4)!=p||read(e,p+4)!=h))throw new Exception("Motion alias back-links missing");
   }
   if(alias&&(read(e,group+4)!=owner||read(e,owner+4)!=group))throw new Exception("Group back-links missing");
   return "{\"members\":"+count+",\"alias_copy\":"+alias+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=1)throw new Exception("Supply NEW output path");
  Path output=Paths.get(args[0]);if(Files.exists(output))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x16078))!=0x4bfffead||getInt(toAddr(0x1c818))!=0x4bff55b9||getInt(toAddr(0x11dd0))!=0x80040024)
   throw new Exception("Unsupported native group revision");
  List<String> rows=new ArrayList<>();for(int n:new int[]{1,2,4})for(boolean alias:new boolean[]{false,true})rows.add(trace(n,alias));
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native motion groups: "+rows.size()+" cases passed");
 }
}
