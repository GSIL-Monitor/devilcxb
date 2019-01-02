public class Recursive_new {

    private static int fab(int index) {
        if (index == 1 || index == 2) {
            return 1;
        } else {
            return fab(index - 1) + fab(index - 2);
        }
    }

    public static void main(String arg[]) {
        System.out.println(fab(4));
    }
}
