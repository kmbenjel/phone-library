// Read-only dump of a Shamela Lucene store (book cards, author bios) as JSON lines.
// Compiled with any javac >= 11 (no Lucene types at compile time: reflection), run on Shamela's own Java 21 with its
// Lucene 10.4 jars:  JAVA=~/.local/share/shamela/app/linux/64/jre/2/bin/java
//   $JAVA -cp "tools/shamela-dump:$HOME/.local/share/shamela/app/lucene/2/*" Dump <store dir> > out.jsonl
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;

public class Dump {
    static String esc(String s) {
        StringBuilder b = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            if (c == '"' || c == '\\') b.append('\\').append(c);
            else if (c == '\n') b.append("\\n");
            else if (c == '\r') b.append("\\r");
            else if (c == '\t') b.append("\\t");
            else if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
            else b.append(c);
        }
        return b.append('"').toString();
    }
    public static void main(String[] a) throws Exception {
        Class<?> fs = Class.forName("org.apache.lucene.store.FSDirectory");
        Object dir = fs.getMethod("open", Path.class).invoke(null, Paths.get(a[0]));
        Class<?> dr = Class.forName("org.apache.lucene.index.DirectoryReader");
        Class<?> dirc = Class.forName("org.apache.lucene.store.Directory");
        Object reader = dr.getMethod("open", dirc).invoke(null, dir);
        int max = (int) reader.getClass().getMethod("maxDoc").invoke(reader);
        Object stored = reader.getClass().getMethod("storedFields").invoke(reader);
        Method doc = stored.getClass().getMethod("document", int.class);
        doc.setAccessible(true);
        Object live = Class.forName("org.apache.lucene.index.MultiBits").getMethod("getLiveDocs",
            Class.forName("org.apache.lucene.index.IndexReader")).invoke(null, reader);
        Method get = live == null ? null : live.getClass().getMethod("get", int.class);
        if (get != null) get.setAccessible(true);
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < max; i++) {
            if (get != null && !(boolean) get.invoke(live, i)) continue;
            Object d = doc.invoke(stored, i);
            List<?> fields = (List<?>) d.getClass().getMethod("getFields").invoke(d);
            out.setLength(0); out.append('{');
            boolean first = true;
            for (Object f : fields) {
                String name = (String) f.getClass().getMethod("name").invoke(f);
                Object sv = f.getClass().getMethod("stringValue").invoke(f);
                Object nv = f.getClass().getMethod("numericValue").invoke(f);
                String val = sv != null ? esc((String) sv) : (nv != null ? esc(nv.toString()) : "null");
                if (!first) out.append(',');
                out.append(esc(name)).append(':').append(val); first = false;
            }
            System.out.println(out.append('}'));
        }
    }
}
