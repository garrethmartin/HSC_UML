using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConnectedComponents
{
    public class PositionComparerX : IComparer<Position>
    {
        public int Compare(Position one, Position two)
        {
            if (one == null && two == null)
                return 0; // they are equal
            if (one == null && two != null)
                return -1; // two is greater
            if (one != null && two == null)
                return 1; // one is greater

            int retval = one.X.CompareTo(two.X);
            if (retval != 0)
                return retval; // not equal so return 

            // X is equal so sort on second key of Y
            return one.Y.CompareTo(two.Y);
        }
    }

}
