// Native jump-pair lane and CH gameplay metadata consumption, synthetic inputs.
// Args: nba-2k11|college-hoops-2k8 NEW_OUTPUT_JSON. No game/file mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
public class NativeJumpGameplayTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,int value){e.writeMemoryValue(toAddr(at),4,value);}
 private int read(EmulatorHelper e,long at){return ByteBuffer.wrap(e.readMemory(toAddr(at),4)).getInt();}
 private String donor(int bit) throws Exception {
  if(getInt(toAddr(0x4993c8))!=0x2e030000||getInt(toAddr(0x499474))!=0x481bd679)throw new Exception("Unsupported donor jump-pair revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long payload=0x40004000L;e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   word(e,payload,1);word(e,payload+4,0);word(e,payload+8,0x50000000);
   word(e,payload+12,2);word(e,payload+16,0);word(e,payload+20,0x50000100);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);e.writeRegister("xer_so",0);
   e.writeRegister("r3",bit);e.writeRegister("r11",payload);e.writeRegister(e.getPCRegister(),0x4993c8L);
   for(int step=0;step<40;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==0x4993ccL){e.writeRegister("r3",payload);e.writeRegister(e.getPCRegister(),0x499468L);continue;}
    if(pc==0x499478L){
     int expected=bit==1?0x50000000:0x50000100;
     if(e.readRegister("r3").intValue()!=expected)throw new Exception("Donor jump lane mismatch");
     return "{\"profile\":\"nba-2k11\",\"bit\":"+bit+",\"slot\":"+(bit==1?0:1)+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Donor instruction failure: "+e.getLastError());
   }
   throw new Exception("Donor jump lane instruction bound exceeded");
  }finally{e.dispose();}
 }
 private String target(int bit,int style) throws Exception {
  if(getInt(toAddr(0x3247dc))!=0x81023b40||getInt(toAddr(0x743eb0))!=0x80630084)throw new Exception("Unsupported CH gameplay row revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long actor=0x40002000L,player=0x40003000L,state=0x40004000L,table=0x40008000L,perActor=0x40006000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   word(e,actor+0x64,(int)player);word(e,actor+0x70,5);
   // Clear the tested flag first, retaining unrelated player bits.
   word(e,player+0x84,(0x12345678&~(1<<25))|(bit<<25));
   e.writeMemoryValue(toAddr(player+0x73),1,style);
   word(e,0xa58608L,(int)table);word(e,0xa586fcL,(int)perActor);
   long row=table+40*style;
   word(e,row+4,25);word(e,row+8,-25);word(e,row+12,15);
   word(e,row+16,Float.floatToRawIntBits(9));word(e,row+20,Float.floatToRawIntBits(1.1f));
   word(e,row+28,0x1234567);word(e,row+32,0x50000000);word(e,row+36,0x50000100);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0xa54ac8L);e.writeRegister("r3",actor);e.writeRegister("LR",0x40007000L);
   e.writeRegister("r30",0);e.writeRegister("r31",0);
   e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x32479cL);
   for(int step=0;step<128;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==0x2351d0L){e.writeRegister("r3",state);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
    if(pc==0x324890L){
     if(read(e,state+0x104)!=Float.floatToRawIntBits(9)||read(e,state+0xe4)!=15
       ||read(e,state+0xd8)!=(bit==1?25:-25)||read(e,state+0x74)!=(bit==1?0x50000000:0x50000100)
       ||read(e,state+0x8c)!=0||read(e,state+0x48)!=Float.floatToRawIntBits(1.1f)
       ||read(e,perActor+5*28+4)!=0x1234567)throw new Exception("CH gameplay row consumption mismatch");
     if(e.readRegister("r2").longValue()!=0xa54ac8L)throw new Exception("TOC restore failed");
     return "{\"profile\":\"college-hoops-2k8\",\"bit\":"+bit+",\"style\":"+style+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("CH instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   throw new Exception("CH gameplay row instruction bound exceeded");
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=2)throw new Exception("Choose profile and NEW JSON path");
  Path output=Paths.get(args[1]);if(Files.exists(output))throw new Exception("Existing output refused");
  List<String> rows=new ArrayList<>();
  if(args[0].equals("nba-2k11"))for(int bit=0;bit<2;bit++)rows.add(donor(bit));
  else if(args[0].equals("college-hoops-2k8"))for(int bit=0;bit<2;bit++)for(int style:new int[]{0,111,255})rows.add(target(bit,style));
  else throw new Exception("Unsupported profile");
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native jump gameplay consumers: "+rows.size()+" cases passed");
 }
}
