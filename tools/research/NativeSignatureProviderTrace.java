// Native signature selector code -> registry category and player key field.
// Args: NEW_OUTPUT_JSON. Registry lookup services use synthetic manager/results.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeSignatureProviderTrace extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=1)throw new Exception("Supply NEW output path");
  Path output=Paths.get(args[0]);if(Files.exists(output))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x657824))!=0x2b830028||getInt(toAddr(0x657b1c))!=0x3860000e
      ||getInt(toAddr(0x657b24))!=0x809e0124)throw new Exception("Unsupported provider revision");
  int[] categories={0,1,1,1,1,1,1,1,1,1,1,2,3,4,5,6,11,12,13,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,7,10,9,8};
  int[] fields={0xd4,0xd8,0xdc,0xe0,0xe4,0xe8,0xec,0xf0,0xf4,0xf8,0xfc,0x100,0x104,0x108,0x10c,0x110,0x154,0x158,0x15c,0x160,0x124,0x128,0x12c,0x130,0x134,0x138,0x13c,0x140,0x144,0x148,0x14c,0x150,0x164,0x168,0x16c,0x170,0x174,0x11c,0x114,0x118,0x120};
  List<String> rows=new ArrayList<>();
  for(int selector=0;selector<41;selector++)for(int alternate=0;alternate<2;alternate++){
   EmulatorHelper e=new EmulatorHelper(currentProgram);
   try {
    long player=0x40003000L,manager=0x40005000L;
    e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
    for(int field=0xd4;field<=0x174;field+=4)e.writeMemoryValue(toAddr(player+field),4,0x70000000+field);
    e.writeRegister("LR",0x40007000L);e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);e.writeRegister("xer_so",0);
    e.writeRegister("r3",selector);e.writeRegister("r4",player);e.writeRegister("r5",alternate);
    e.writeRegister(e.getPCRegister(),0x657824L);boolean categorySeen=false,done=false;
    for(int step=0;step<96;step++){
     long pc=e.getExecutionAddress().getOffset();
     if(pc==0x945120L){e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;}
     if(pc==0x659790L){
      if(e.readRegister("r3").intValue()!=categories[selector])throw new Exception("Registry category mismatch");
      categorySeen=true;e.writeRegister("r3",manager);e.writeRegister(e.getPCRegister(),e.readRegister("LR"));continue;
     }
     if(pc==0x659730L){
      int field=fields[selector];
      if(alternate!=0){
       if(selector==16||selector==18||selector==30||selector==32||selector==34)field+=4;
       if(selector==17||selector==19||selector==31||selector==33||selector==35)field-=4;
      }
      if(!categorySeen||e.readRegister("r3").longValue()!=manager||e.readRegister("r4").intValue()!=0x70000000+field)throw new Exception("Player field mismatch");
      rows.add("{\"selector\":"+selector+",\"alternate\":"+alternate+",\"registry_category\":"+categories[selector]+",\"player_key_offset\":"+field+",\"passed\":true}");done=true;break;
     }
     if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
    }
    if(!done)throw new Exception("Provider instruction bound exceeded");
   }finally{e.dispose();}
  }
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native signature provider: "+rows.size()+" cases passed");
 }
}

