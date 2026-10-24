// Bounded native shot-family selection, synthetic cached resources only.
// Args: nba-2k11|college-hoops-2k8 NEW_OUTPUT_JSON. No game or executable writes.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

public class NativeShotFamilyTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,int v){e.writeMemoryValue(toAddr(at),4,v);}
 private int read(EmulatorHelper e,long at){return ByteBuffer.wrap(e.readMemory(toAddr(at),4)).getInt();}
 private String donor(int bit,int kind,boolean empty) throws Exception {
  if(getInt(toAddr(0x653658))!=0x48003495 ||getInt(toAddr(0x6537d4))!=0x48003319
     ||getInt(toAddr(0x656aec))!=0x81630004 ||getInt(toAddr(0x949cf0))!=0x806300cc)
   throw new Exception("Unsupported NBA11 shot-family revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   long cache=0x40002000L,player=0x40003000L,payload=0x40004000L,entry=0x40005000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   word(e,player+0xcc,0x2468ace0|bit);word(e,player+0xd4,17);word(e,entry+8,(int)payload);
   for(int slot=0;slot<8;slot++){
    long group=0x40006000L+slot*0x80;
    word(e,payload+slot*12,empty&&slot<2?0:slot+1);
    word(e,payload+slot*12+4,kind);
    int direct=empty&&slot<2?0:0x50000000+slot*0x100;
    word(e,payload+slot*12+8,kind==0?direct:(int)group);
    for(int member=0;member<4;member++)word(e,group+member*16+12,0x51000000+slot*0x100+member);
   }
   word(e,payload+96,0); // Only supplied index zero is certified here.
   e.writeRegister("xer_so",0);e.writeRegister("r1",0x40001000L);
   e.writeRegister("r2",0x40f2a98L);
   e.writeRegister("r8",player);e.writeRegister("r26",player);e.writeRegister("r31",cache);
   e.writeRegister(e.getPCRegister(),0x653610L);
   boolean lookup=false;List<Integer> slots=new ArrayList<>();
   for(int step=0;step<256;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==0x657824L){
     if(e.readRegister("r3").intValue()!=0||e.readRegister("r4").longValue()!=player)
      throw new Exception("Unexpected signature lookup arguments");
     lookup=true;e.writeRegister("r3",entry);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;
    }
    if(pc==0x6536b8L){
     if(!lookup)throw new Exception("Signature lookup missing");
     for(int pair=0;pair<4;pair++){
      int slot=pair*2+(bit==0?1:0);slots.add(slot);
      int expected=kind==5?0:kind==0?(empty&&slot<2?0:0x50000000+slot*0x100):0x51000000+slot*0x100+kind-1;
      if(read(e,cache+8+pair*4)!=expected)throw new Exception("Donor pair selection mismatch");
     }
     if(read(e,cache+0x18)!=getInt(toAddr(0xa51564)))throw new Exception("Control-word index read mismatch");
     return "{\"profile\":\"nba-2k11\",\"selector_bit\":"+bit+",\"kind\":"+kind+",\"empty_first_pair\":"+empty+",\"selected_slots\":"+slots+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   throw new Exception("Donor shot-family prefix exceeded instruction bound");
  }finally{e.dispose();}
 }
 private String target(int bit) throws Exception {
  if(getInt(toAddr(0x3213d4))!=0x81623b40||getInt(toAddr(0x3213ec))!=0x80690004)
   throw new Exception("Unsupported CH shot-pair revision");
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try {
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
   word(e,0xa58608L,0x40004000);word(e,0x40004020L,0x60000000);word(e,0x40004024L,0x60000100);
   e.writeRegister("xer_so",0);e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0xa54ac8L);
   e.writeRegister("r28",0);e.writeRegister("r29",bit);e.writeRegister("r30",0);
   e.writeRegister(e.getPCRegister(),0x3213b8L);
   for(int step=0;step<64;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==(bit==0?0x3213f0L:0x321488L)){
     int expected=bit==0?0x60000100:0x60000000;
     if(e.readRegister("r3").intValue()!=expected)throw new Exception("Target pair ordering mismatch");
     return "{\"profile\":\"college-hoops-2k8\",\"selector_bit\":"+bit+",\"row_header_offset\":"+(bit==0?36:32)+",\"passed\":true}";
    }
    if(!e.step(monitor))throw new Exception("Target instruction failure: "+e.getLastError());
   }
   throw new Exception("Target pair selector exceeded instruction bound");
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=2)throw new Exception("Choose profile and NEW JSON path");
  Path output=Paths.get(args[1]).toAbsolutePath().normalize();
  if(Files.exists(output))throw new Exception("Source/existing report overwrite refused");
  List<String> rows=new ArrayList<>();
  if(args[0].equals("nba-2k11")){
   for(int bit=0;bit<2;bit++)for(int kind=0;kind<=5;kind++)rows.add(donor(bit,kind,false));
   for(int bit=0;bit<2;bit++)rows.add(donor(bit,0,true));
  }else if(args[0].equals("college-hoops-2k8")){
   rows.add(target(0));rows.add(target(1));
  }else throw new Exception("Unestablished profile");
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native animation shot-family selection: "+rows.size()+" cases passed");
 }
}
