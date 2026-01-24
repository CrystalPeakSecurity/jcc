/*
 * JCC Test Client - loads and tests applets on the JavaCard simulator
 */

import java.io.FileInputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.Security;
import java.util.List;
import java.util.Properties;

import javax.smartcardio.Card;
import javax.smartcardio.CardChannel;
import javax.smartcardio.CardTerminal;
import javax.smartcardio.CommandAPDU;
import javax.smartcardio.ResponseAPDU;
import javax.smartcardio.TerminalFactory;

import com.oracle.javacard.ams.AMService;
import com.oracle.javacard.ams.AMServiceFactory;
import com.oracle.javacard.ams.AMSession;
import com.oracle.javacard.ams.config.AID;
import com.oracle.javacard.ams.config.CAPFile;
import com.oracle.smartcardio.socket.SocketCardTerminalProvider;

public class JCCClient {

    static {
        // Register the socket card terminal provider
        Security.addProvider(new SocketCardTerminalProvider());
    }

    static final String ISD_AID = "aid:A000000151000000";
    static String HOST = "localhost";
    static int PORT = 9025;
    static boolean JSON_OUTPUT = false;

    public static void main(String[] args) {
        if (args.length < 1) {
            printUsage();
            System.exit(1);
        }

        // Check for --json flag
        int argOffset = 0;
        if (args[0].equals("--json")) {
            JSON_OUTPUT = true;
            argOffset = 1;
        }

        if (args.length <= argOffset) {
            printUsage();
            System.exit(1);
        }

        String command = args[argOffset];

        try {
            switch (command) {
                case "test-connection":
                    testConnection();
                    break;
                case "load":
                    if (args.length < argOffset + 5) {
                        System.err.println("Usage: load <cap-file> <pkg-aid> <class-aid> <instance-aid>");
                        System.exit(1);
                    }
                    loadApplet(args[argOffset + 1], args[argOffset + 2], args[argOffset + 3], args[argOffset + 4]);
                    break;
                case "unload":
                    if (args.length < argOffset + 3) {
                        System.err.println("Usage: unload <pkg-aid> <instance-aid>");
                        System.exit(1);
                    }
                    unloadApplet(args[argOffset + 1], args[argOffset + 2]);
                    break;
                case "send":
                    if (args.length < argOffset + 3) {
                        System.err.println("Usage: send <instance-aid> <apdu-hex>");
                        System.exit(1);
                    }
                    sendApdu(args[argOffset + 1], args[argOffset + 2]);
                    break;
                case "session":
                    if (args.length < argOffset + 2) {
                        System.err.println("Usage: session <instance-aid>");
                        System.exit(1);
                    }
                    runSession(args[argOffset + 1]);
                    break;
                case "test-counter":
                    if (args.length < argOffset + 2) {
                        System.err.println("Usage: test-counter <cap-file>");
                        System.exit(1);
                    }
                    testCounterApplet(args[argOffset + 1]);
                    break;
                default:
                    System.err.println("Unknown command: " + command);
                    printUsage();
                    System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    static void printUsage() {
        System.out.println("JCC Test Client");
        System.out.println("Usage:");
        System.out.println("  test-connection                              - Test simulator connection");
        System.out.println("  load <cap> <pkg-aid> <class-aid> <inst-aid>  - Load and install applet");
        System.out.println("  unload <pkg-aid> <inst-aid>                  - Uninstall and unload applet");
        System.out.println("  send <inst-aid> <apdu-hex>                   - Send APDU to applet");
        System.out.println("  session <inst-aid>                           - Interactive session (reads APDUs from stdin)");
        System.out.println("  test-counter <cap>                           - Run counter applet test");
    }

    static CardTerminal getTerminal() throws Exception {
        TerminalFactory tf = TerminalFactory.getInstance(
            "SocketCardTerminalFactoryType",
            List.of(new InetSocketAddress(HOST, PORT)),
            "SocketCardTerminalProvider"
        );
        return tf.terminals().list().get(0);
    }

    static AMService getAMService() throws Exception {
        AMService ams = AMServiceFactory.getInstance("GP2.2");
        // Set default SCP03 keys
        Properties props = new Properties();
        props.setProperty("A000000151000000_scp03enc_01", "404142434445464748494A4B4C4D4E4F");
        props.setProperty("A000000151000000_scp03mac_01", "404142434445464748494A4B4C4D4E4F");
        props.setProperty("A000000151000000_scp03dek_01", "404142434445464748494A4B4C4D4E4F");
        ams.setProperties(props);
        return ams;
    }

    static void testConnection() throws Exception {
        System.out.println("Connecting to simulator at " + HOST + ":" + PORT + "...");
        CardTerminal terminal = getTerminal();

        if (terminal.waitForCardPresent(5000)) {
            Card card = terminal.connect("*");
            byte[] atr = card.getATR().getBytes();
            System.out.println("Connected! ATR: " + bytesToHex(atr));
            card.disconnect(true);
            System.out.println("Connection test passed.");
        } else {
            System.err.println("Failed to connect to simulator");
            System.exit(1);
        }
    }

    static void loadApplet(String capPath, String pkgAid, String classAid, String instanceAid) throws Exception {
        System.out.println("Loading applet from: " + capPath);

        CAPFile capFile = CAPFile.from(capPath);
        AMService ams = getAMService();
        CardTerminal terminal = getTerminal();

        if (!terminal.waitForCardPresent(5000)) {
            throw new IOException("Failed to connect to simulator");
        }

        Card card = terminal.connect("*");
        System.out.println("Connected, ATR: " + bytesToHex(card.getATR().getBytes()));

        String sPkgAid = "aid:" + pkgAid;
        String sClassAid = "aid:" + classAid;
        String sInstanceAid = "aid:" + instanceAid;

        System.out.println("Installing applet...");
        System.out.println("  Package AID:  " + pkgAid);
        System.out.println("  Class AID:    " + classAid);
        System.out.println("  Instance AID: " + instanceAid);

        AMSession session = ams.openSession(ISD_AID)
           .load(sPkgAid, capFile.getBytes())
           .install(sPkgAid, sClassAid, sInstanceAid)
           .close();

        // Actually run the session through the card channel
        @SuppressWarnings("unchecked")
        java.util.List<ResponseAPDU> responses = (java.util.List<ResponseAPDU>) session.run(card.getBasicChannel());

        // Check for errors in responses
        for (ResponseAPDU resp : responses) {
            int sw = resp.getSW();
            if (sw != 0x9000) {
                card.disconnect(true);
                throw new RuntimeException("Load/install failed with SW=" + String.format("%04X", sw));
            }
        }

        card.disconnect(true);
        System.out.println("Applet installed successfully.");
    }

    static void unloadApplet(String pkgAid, String instanceAid) throws Exception {
        System.out.println("Unloading applet...");

        AMService ams = getAMService();
        CardTerminal terminal = getTerminal();

        if (!terminal.waitForCardPresent(5000)) {
            throw new IOException("Failed to connect to simulator");
        }

        Card card = terminal.connect("*");

        String sPkgAid = "aid:" + pkgAid;
        String sInstanceAid = "aid:" + instanceAid;

        AMSession session = ams.openSession(ISD_AID)
           .uninstall(sInstanceAid)
           .unload(sPkgAid)
           .close();

        session.run(card.getBasicChannel());

        card.disconnect(true);
        System.out.println("Applet unloaded successfully.");
    }

    static void sendApdu(String instanceAid, String apduHex) throws Exception {
        CardTerminal terminal = getTerminal();

        if (!terminal.waitForCardPresent(5000)) {
            throw new IOException("Failed to connect to simulator");
        }

        Card card = terminal.connect("*");
        CardChannel channel = card.getBasicChannel();

        // Select the applet
        byte[] aidBytes = AID.from("aid:" + instanceAid).toBytes();
        CommandAPDU selectApdu = new CommandAPDU(0x00, 0xA4, 0x04, 0x00, aidBytes, 256);
        ResponseAPDU selectResponse = channel.transmit(selectApdu);
        if (!JSON_OUTPUT) {
            System.out.println("SELECT: " + String.format("%04X", selectResponse.getSW()));
        }

        if (selectResponse.getSW() != 0x9000) {
            card.disconnect(true);
            throw new RuntimeException("Failed to select applet: " + String.format("%04X", selectResponse.getSW()));
        }

        // Send the APDU
        byte[] apduBytes = hexToBytes(apduHex);
        CommandAPDU apdu = new CommandAPDU(apduBytes);
        if (!JSON_OUTPUT) {
            System.out.println("SEND: " + apduHex);
        }

        ResponseAPDU response = channel.transmit(apdu);

        if (JSON_OUTPUT) {
            // Output JSON format: {"data":"<hex>","sw":<int>}
            System.out.println("{\"data\":\"" + bytesToHex(response.getData()) +
                             "\",\"sw\":" + response.getSW() + "}");
        } else {
            System.out.println("RECV: " + bytesToHex(response.getData()) + " SW=" + String.format("%04X", response.getSW()));
        }

        card.disconnect(false);  // Don't reset card - preserves transient memory
    }

    static void runSession(String instanceAid) throws Exception {
        // Interactive session mode - keeps connection open and reads APDUs from stdin
        // Each line should be an APDU in hex format
        // Outputs JSON responses: {"data":"<hex>","sw":<int>}
        // Send empty line or "quit" to exit

        CardTerminal terminal = getTerminal();

        if (!terminal.waitForCardPresent(5000)) {
            throw new IOException("Failed to connect to simulator");
        }

        Card card = terminal.connect("*");
        CardChannel channel = card.getBasicChannel();

        // Select the applet once at session start
        byte[] aidBytes = AID.from("aid:" + instanceAid).toBytes();
        CommandAPDU selectApdu = new CommandAPDU(0x00, 0xA4, 0x04, 0x00, aidBytes, 256);
        ResponseAPDU selectResponse = channel.transmit(selectApdu);

        if (selectResponse.getSW() != 0x9000) {
            card.disconnect(false);
            throw new RuntimeException("Failed to select applet: " + String.format("%04X", selectResponse.getSW()));
        }

        // Signal ready
        System.out.println("{\"ready\":true}");
        System.out.flush();

        // Read APDUs from stdin
        java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        String line;
        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty() || line.equals("quit")) {
                break;
            }

            try {
                byte[] apduBytes = hexToBytes(line);
                CommandAPDU apdu = new CommandAPDU(apduBytes);
                ResponseAPDU response = channel.transmit(apdu);

                System.out.println("{\"data\":\"" + bytesToHex(response.getData()) +
                                 "\",\"sw\":" + response.getSW() + "}");
            } catch (Exception e) {
                System.out.println("{\"error\":\"" + e.getMessage().replace("\"", "'") + "\"}");
            }
            System.out.flush();
        }

        card.disconnect(false);
    }

    static void testCounterApplet(String capPath) throws Exception {
        String pkgAid = "A00000006203010105";
        String classAid = "A0000000620301010501";
        String instanceAid = "A0000000620301010501";

        System.out.println("=== Counter Applet Test ===\n");

        // Load the applet
        loadApplet(capPath, pkgAid, classAid, instanceAid);
        System.out.println();

        try {
            CardTerminal terminal = getTerminal();
            if (!terminal.waitForCardPresent(5000)) {
                throw new IOException("Failed to connect");
            }

            Card card = terminal.connect("*");
            CardChannel channel = card.getBasicChannel();

            // Select the applet
            byte[] aidBytes = AID.from("aid:" + instanceAid).toBytes();
            CommandAPDU selectApdu = new CommandAPDU(0x00, 0xA4, 0x04, 0x00, aidBytes, 256);
            ResponseAPDU selectResponse = channel.transmit(selectApdu);
            System.out.println("SELECT applet: SW=" + String.format("%04X", selectResponse.getSW()));

            if (selectResponse.getSW() != 0x9000) {
                throw new RuntimeException("Failed to select applet");
            }

            // Test INCREMENT (INS=0x01) on counter 0
            System.out.println("\nIncrementing counter 0 three times:");
            for (int i = 0; i < 3; i++) {
                // CLA=0x80, INS=0x01, P1=0x00 (counter index), P2=0x00
                CommandAPDU incApdu = new CommandAPDU(0x80, 0x01, 0x00, 0x00, 256);
                ResponseAPDU incResponse = channel.transmit(incApdu);
                int value = ((incResponse.getData()[0] & 0xFF) << 8) | (incResponse.getData()[1] & 0xFF);
                System.out.println("  Counter[0] = " + value + " (SW=" + String.format("%04X", incResponse.getSW()) + ")");
            }

            // Test INCREMENT on counter 1
            System.out.println("\nIncrementing counter 1 twice:");
            for (int i = 0; i < 2; i++) {
                CommandAPDU incApdu = new CommandAPDU(0x80, 0x01, 0x01, 0x00, 256);
                ResponseAPDU incResponse = channel.transmit(incApdu);
                int value = ((incResponse.getData()[0] & 0xFF) << 8) | (incResponse.getData()[1] & 0xFF);
                System.out.println("  Counter[1] = " + value + " (SW=" + String.format("%04X", incResponse.getSW()) + ")");
            }

            card.disconnect(true);
            System.out.println("\n=== Test Passed ===");

        } finally {
            // Cleanup - unload the applet
            System.out.println("\nCleaning up...");
            unloadApplet(pkgAid, instanceAid);
        }
    }

    static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }

    static byte[] hexToBytes(String hex) {
        hex = hex.replaceAll("\\s+", "");
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                                 + Character.digit(hex.charAt(i+1), 16));
        }
        return data;
    }
}
