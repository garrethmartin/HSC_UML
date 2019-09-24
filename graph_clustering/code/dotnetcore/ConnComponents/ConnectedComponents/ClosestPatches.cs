using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConnectedComponents
{
    internal class ClosestPatches
    {
        List<Position> allPosSortedX = null;
        PositionComparerX pcX = null;
        int windowSize = -1;
        int maxDistance = -1;
        List<int> sigmaMask = null;

        internal ClosestPatches(List<Position> allPosSortedX, List<int> sigmaMask, PositionComparerX pcX, int windowSize, int maxDistance)
        {
            this.pcX = pcX;
            this.allPosSortedX = allPosSortedX;
            this.windowSize = windowSize;
            //this.maxDistance = (windowSize * 2) + 1;
            this.maxDistance = maxDistance;
            this.sigmaMask = sigmaMask;
        }

        internal Dictionary<int, Position> GetOverlappingPatches(Position position, int windowSize)
        {
            var overlap = new Dictionary<int, Position>();

            GetClosestX(overlap, allPosSortedX, position);

            return overlap;
        }

        private void Validate2(List<Position> one, List<Position> two)
        {
            if (one.Count > two.Count)
            {
                Console.WriteLine("switching");
                List<Position> t = one;
                one = two;
                two = t;
            }
            for (int i = 0; i < one.Count; i++)
            {
                int found = 0;
                for (int j = 0; j < two.Count; j++)
                {
                    if (one[i].Index == two[j].Index)
                        found += 1;
                }

                if (found > 0)
                {
                    //Console.WriteLine("found: {0} {1} {2}", i, found, one[i].ToString());
                }
                else
                {
                    Console.WriteLine("NOT found: {0} ", one[i].ToString());
                }
            }

        }

        private void Validate(List<Position> positions, Position position)
        {
            foreach (Position pos in positions)
            {
                if (!Overlaps(position, pos))
                {
                    int xDist = Math.Abs(position.X - pos.X);
                    int yDist = Math.Abs(position.Y - pos.Y);
                    Console.WriteLine("{0} {1}", xDist, yDist); 
                    if (xDist > maxDistance || yDist > maxDistance)
                        throw new Exception(pos.ToString());
                }
            }

        }

        private void GetClosestX(Dictionary<int, Position> overlappingPatches, List<Position> allPosSortedX, Position position)
        {
            int xIndex = GetIndexOfNearest(allPosSortedX, this.pcX, position);

            // loop back   
            int indexFrom = xIndex;
            int patchDistanceX = 0;
            int patchDistanceY = 0;
            while (indexFrom > 0 && patchDistanceX <= maxDistance)
            {
                Position tempPos = allPosSortedX[indexFrom];

                if (sigmaMask[tempPos.Index] == 0)
                {
                    // pixel is threholded so doesn't 'exist'
                    indexFrom--;
                    continue;
                }

                // calculate the difference between the two position axes, if any is bigger than max distance
                // then not overlapping.
                patchDistanceX = Math.Abs(position.X - tempPos.X);
                patchDistanceY = Math.Abs(position.Y - tempPos.Y);
                if (patchDistanceX <= maxDistance && patchDistanceY <= maxDistance)
                {
                    if (!overlappingPatches.ContainsKey(tempPos.Index))
                    {
                        overlappingPatches.Add(tempPos.Index, tempPos);
                        //hacProximityCounts[position.HACCluster, tempPos.HACCluster] += 1;
                    }
                }

                indexFrom--;
            }

            // loop forward
            indexFrom = xIndex + 1;
            patchDistanceX = 0;
            patchDistanceY = 0;
            while (indexFrom < allPosSortedX.Count && patchDistanceX <= maxDistance)
            {
                Position tempPos = allPosSortedX[indexFrom];
                if (sigmaMask[tempPos.Index] == 0)
                {
                    // pixel is threholded so doesn't 'exist'
                    indexFrom++;
                    continue;
                }


                patchDistanceX = Math.Abs(position.X - tempPos.X);
                patchDistanceY = Math.Abs(position.Y - tempPos.Y);
                if (patchDistanceX <= maxDistance && patchDistanceY <= maxDistance)
                {
                    if (!overlappingPatches.ContainsKey(tempPos.Index))
                    {
                        overlappingPatches.Add(tempPos.Index, tempPos);
                        //hacProximityCounts[position.HACCluster, tempPos.HACCluster] += 1;
                    }
                }


                indexFrom++;
            }
        }


        private int GetIndexOfNearest(List<Position> positions, IComparer<Position> comparer, Position pos)
        {
            int indexFrom = positions.BinarySearch(pos, comparer);
            if (indexFrom < 0)
            {
                int indexOfNearest = ~indexFrom;
                if (indexOfNearest == positions.Count)
                    return positions.Count - 1;
                
                if (indexOfNearest == 0)
                    indexFrom = 0;
                else
                    // from time is between (indexOfNearest - 1) and indexOfNearest
                    indexFrom = indexOfNearest;
            }

            return indexFrom;
        }

        private bool Overlaps(Position one, Position two)
        {
            //if (RectA.X1 < RectB.X2 && RectA.X2 > RectB.X1 &&
            //    RectA.Y1 < RectB.Y2 && RectA.Y2 > RectB.Y1) 

            int oneX1 = one.X - windowSize;
            int oneX2 = one.X + windowSize;
            int oneY1 = one.Y - windowSize;
            int oneY2 = one.Y + windowSize;

            int twoX1 = two.X - windowSize;
            int twoX2 = two.X + windowSize;
            int twoY1 = two.Y - windowSize;
            int twoY2 = two.Y + windowSize;

            if (oneX1 < twoX2 && oneX2 > twoX1 &&
                oneY1 < twoY2 && oneY2 > twoY1)
                return true;

            return false;
        }
    }
}

