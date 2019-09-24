using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConnectedComponents
{
    public class PositionComparerY : IComparer<Position>
    {
        public int Compare(Position one, Position two)
        {
            if (one == null && two == null)
                return 0; // they are equal
            if (one == null && two != null)
                return -1; // two is greater
            if (one != null && two == null)
                return 1; // one is greater

            int retval = one.Y.CompareTo(two.Y);
            if (retval != 0)
                return retval; // not equal so return 

            // Y is equal so sort on second key of X
            return one.X.CompareTo(two.X);
        }
    }
}
