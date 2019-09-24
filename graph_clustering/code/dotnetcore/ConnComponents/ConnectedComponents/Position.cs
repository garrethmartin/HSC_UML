using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConnectedComponents
{
    public class Position : IComparable<Position>
    {
        public int X;
        public int Y;
        public int Image;
        public int Index;
        public int Label;
        public int ObjectId;
        public int HACCluster;
        public int GNGCluster;

        public Position(int index, int[] coordinates)
        {
            this.Image = coordinates[0];
            this.X = coordinates[1];
            this.Y = coordinates[2];
            this.Index = index;
            this.Label = -1;
            this.ObjectId = -1;
        }

        public override string ToString()
        {
            return "Index: " + Index + " Img: " + Image + " X: " + X + " Y: " + Y;
        }
        
        public int CompareTo(Position comparePos)
        {
            // A null value means that this object is greater. 
            if (comparePos == null)
                return 1;
            else
                return this.Index.CompareTo(comparePos.Index);
        }

        public static int SortByIndex(Position one, Position two)
        {
            if (one == null && two == null)
                return 0; // they are equal
            if (one == null && two != null)
                return -1; // two is greater
            if (one != null && two == null)
                return 1; // one is greater

            int retval = one.Index.CompareTo(two.Index);
            if (retval != 0)
                return retval; // not equal so return 

            // Index is equal so sort on second key of Index
            return one.Index.CompareTo(two.Index);
        }

    }
}
