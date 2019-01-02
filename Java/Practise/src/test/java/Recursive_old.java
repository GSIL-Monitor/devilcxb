import java.util.ArrayList;

public class Recursive_old {

    private static int fab(int index, ArrayList<Integer> list) {
        if (index == 1 || index == 2) {
            return 1;
        } else {
            if (list.size() == index && list.size() > 0) {
//                System.out.println(list.get(0));
                return list.get(list.size() - 1);
            }
            list.add(list.get(list.size() - 1) + list.get(list.size() - 2));
            return fab(index, list);
        }
    }

    public static void main(String args[]) {
        int index = 40;
        ArrayList<Integer> list = new ArrayList<Integer>();
        list.add(1);
        list.add(1);
        System.out.println(fab(index, list));
    }
}
