// Bounded Ghidra p-code checks of the documented CH2K8 recruiting revision.
// Operates only on synthetic emulator memory. Does not save or patch the input.
// Run analyzeHeadless with -readOnly -noanalysis -process EBOOT.ELF
// -postScript RecruitingPoolTrace.java <private report path>.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;

public class RecruitingPoolTrace extends GhidraScript {
    private static final long TOC = 0xa64a94L;
    private static final long FIRST = 0x40010000L, SECOND = 0x40040000L;
    private static final long STATE = 0x40003000L, SCHOOL = 0x40008000L;
    private static final long RECRUIT = 0x40009000L, DONE = 0x40300000L;
    private final List<String> passed = new ArrayList<>();

    private void put(EmulatorHelper e, long a, int size, long value) {
        e.writeMemoryValue(toAddr(a), size, value);
    }

    private long get(EmulatorHelper e, long a, int size) throws Exception {
        byte[] bytes = e.readMemory(toAddr(a), size);
        if (bytes == null || bytes.length != size) throw new Exception("Memory read failed");
        long value = 0;
        for (byte b : bytes) value = (value << 8) | (b & 255);
        return value;
    }

    private EmulatorHelper setup() throws Exception {
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        e.writeMemory(toAddr(0x40000000L), new byte[0x200000]);
        put(e, 0xa616f8L, 4, FIRST);
        put(e, 0xa616fcL, 4, STATE);
        put(e, 0xa61700L, 4, STATE + 4);
        put(e, 0xa61704L, 4, SECOND);
        put(e, 0xa61708L, 4, STATE + 8);
        put(e, 0xa617d8L, 4, STATE + 12);
        put(e, STATE + 12, 1, 1); // Skip one-time message template initialization.
        for (int i = 0; i < 32; i++) e.writeRegister("r" + i, 0);
        for (int i = 0; i < 8; i++) e.writeRegister("cr" + i, 0);
        e.writeRegister("xer_so", 0);
        e.writeRegister("r1", 0x40100000L);
        e.writeRegister("r2", TOC);
        return e;
    }

    private int call(EmulatorHelper e, long entry, long stop, long... args) throws Exception {
        for (int i = 0; i < args.length; i++) e.writeRegister("r" + (3 + i), args[i]);
        e.writeRegister("LR", DONE);
        e.writeRegister(e.getPCRegister(), entry);
        for (int step = 0; step < 4096; step++) {
            long pc = e.getExecutionAddress().getOffset();
            if (pc == stop) return e.readRegister("r3").intValue();
            if (!e.step(monitor)) throw new Exception("Instruction failure at " +
                Long.toHexString(pc) + ": " + e.getLastError());
        }
        throw new Exception("Instruction limit exceeded");
    }

    private void check(boolean value, String detail) throws Exception {
        if (!value) throw new Exception(detail);
    }

    private void initSecond() throws Exception {
        EmulatorHelper e = setup();
        try {
            byte[] sentinel = new byte[24];
            Arrays.fill(sentinel, (byte) 0xA5);
            e.writeMemory(toAddr(SECOND + 16), sentinel);
            call(e, 0x5c34f0L, DONE, 3);
            check(get(e, SECOND + 24, 4) == 0, "Second initialization pointer");
            check(get(e, SECOND + 28, 2) == 65535, "Second initialization terminator");
            check(get(e, SECOND + 30, 2) == 0, "Second initialization flags");
            check(get(e, SECOND + 16, 8) == 0xA5A5A5A5A5A5A5A5L, "Previous node changed");
            check(get(e, SECOND + 32, 8) == 0xA5A5A5A5A5A5A5A5L, "Next node changed");
            passed.add("second_initialize_preserves_neighbors");
        } finally { e.dispose(); }
    }

    private void freeSecond() throws Exception {
        EmulatorHelper e = setup();
        try {
            put(e, STATE + 8, 4, 5);
            put(e, SECOND + 24, 8, -1);
            call(e, 0x5c3528L, DONE, 3);
            check(get(e, STATE + 8, 4) == 3, "Second free head");
            check(get(e, SECOND + 24, 4) == 0, "Freed pointer not cleared");
            check(get(e, SECOND + 28, 2) == 5, "Second free next");
            check(get(e, SECOND + 30, 2) == 0, "Freed flags not cleared");
            passed.add("second_release_clears_and_links");
        } finally { e.dispose(); }
    }

    private void popFirst(int head, int next, int highwater) throws Exception {
        EmulatorHelper e = setup();
        try {
            put(e, STATE, 4, head);
            put(e, STATE + 4, 4, highwater);
            if (head >= 0) put(e, FIRST + head * 8L + 2, 2, next);
            int returned = call(e, 0x5c3144L, DONE);
            check(returned == head, "First allocation result");
            check((int) get(e, STATE, 4) == (head < 0 ? head : next), "First free head");
            if (head >= 0) {
                check(get(e, FIRST + head * 8L + 2, 2) == 65535, "Allocated node still linked");
                check(get(e, STATE + 4, 4) == Math.max(head, highwater), "Highwater mismatch");
            }
            passed.add("first_pop_" + head);
        } finally { e.dispose(); }
    }

    private void lookup(long target, int head, int expected) throws Exception {
        EmulatorHelper e = setup();
        try {
            put(e, SCHOOL + 0x260, 2, head);
            put(e, SECOND, 4, RECRUIT);
            put(e, SECOND + 4, 2, 1);
            put(e, SECOND + 8, 4, RECRUIT + 216);
            put(e, SECOND + 12, 2, -1);
            int result = call(e, 0x5c3580L, DONE, SCHOOL, target);
            check(result == expected, "School list lookup mismatch");
            passed.add("school_lookup_" + expected + "_head_" + head);
        } finally { e.dispose(); }
    }

    private void clearOffer() throws Exception {
        EmulatorHelper e = setup();
        try {
            put(e, SECOND + 6, 2, 0xABFF);
            call(e, 0x5c36ccL, DONE, 0);
            check(get(e, SECOND + 6, 2) == 0xAB7F, "Offer clear damaged other bits");
            passed.add("offer_clear_preserves_unknown_bits");
        } finally { e.dispose(); }
    }

    private void exhaustedCommitPrefix() throws Exception {
        EmulatorHelper e = setup();
        try {
            put(e, STATE, 4, -1);
            put(e, SCHOOL + 0x2a8, 4, 0xA3001234L);
            put(e, RECRUIT + 0x4a, 2, -1);
            call(e, 0x5c8cd8L, 0x5c8df8L, RECRUIT, SCHOOL, 0);
            check(e.readRegister("r29").intValue() == -1, "Exhausted allocation not propagated");
            check((get(e, RECRUIT + 0x40, 4) & 0x80000000L) != 0, "Commit flag not yet changed");
            check(get(e, SCHOOL + 0x2a8, 4) == 0xA2001234L, "Counter not changed before failed allocation");
            check(get(e, RECRUIT + 0x4a, 2) == 65535, "Interest head unexpected");
            passed.add("commit_prefix_mutates_before_exhausted_allocation");
            // Stop before the following external school-index lookup and invalid node stores.
        } finally { e.dispose(); }
    }

    public void run() throws Exception {
        if (getScriptArgs().length != 1) throw new Exception("Supply a private report path");
        Path output = Paths.get(getScriptArgs()[0]).toAbsolutePath().normalize();
        if (Files.exists(output)) throw new Exception("Choose a new private report path");
        // Revision checks use native TOC topology, not a bundled executable or dump.
        if (getInt(toAddr(0xa616f8L)) - getInt(toAddr(0xa61704L)) != 16000 * 8
            || getInt(toAddr(0xa61788L)) != getInt(toAddr(0xa616f8L)) + 2
            || getInt(toAddr(0xa61784L)) != getInt(toAddr(0xa61704L)) + 4)
            throw new Exception("Unsupported recruiting pool revision");
        initSecond();
        freeSecond();
        popFirst(-1, -1, 0);
        popFirst(0, -1, 0);
        popFirst(15999, -1, 2);
        lookup(RECRUIT + 216, 0, 1);
        lookup(RECRUIT + 432, 0, -1);
        lookup(RECRUIT, -1, -1);
        clearOffer();
        exhaustedCommitPrefix();
        StringBuilder json = new StringBuilder("{\"native_instruction_cases\":[");
        for (int i = 0; i < passed.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(passed.get(i)).append("\"");
        }
        json.append("],\"passed\":").append(passed.size());
        json.append(",\"gameplay_tested\":false,\"input_modified\":false}\n");
        Files.writeString(output, json.toString(), StandardOpenOption.CREATE_NEW);
        println("Recruiting pool native instruction cases: " + passed.size() + " passed");
    }
}
