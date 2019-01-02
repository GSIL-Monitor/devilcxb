import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Test {

    private static int test() {
        ArrayList<Integer> list = new ArrayList<Integer>();
        list.add(1);
        list.add(1);
        return list.get(0);

    }

    public static void main(String args[]) {
        int value = test();
        System.out.println(value);
    }
}
