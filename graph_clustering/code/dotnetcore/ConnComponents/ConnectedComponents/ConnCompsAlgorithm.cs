using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConnectedComponents
{
    internal class ConnCompsAlgorithm
    {

        private ClosestPatches cp = null;
        
        internal ConnCompsAlgorithm(ClosestPatches cp)
        {
            this.cp = cp;
        }

        internal Dictionary<int, List<Position>> Find(List<Position> positions, List<int> sigmaMask,int patchSize)
        {
            int labelCount = 1;
            var allLabels = new Dictionary<int, Label>();
            Dictionary<Position, bool> processedPositions = new Dictionary<Position, bool>();

            for (int i = 0; i < positions.Count; i++)
            {
                Position currPosition = positions[i];
                if (sigmaMask[currPosition.Index] == 0)
                {
                    // pixel is thresholded so skip
                    continue;
                }

                IEnumerable<int> neighbouringLabels = GetNeighbouringLabels(currPosition, patchSize);

                int currentLabel = -1;
                if (!neighbouringLabels.Any())
                {
                    currentLabel = labelCount;
                    allLabels.Add(currentLabel, new Label(currentLabel));
                    labelCount++;
                }
                else
                {
                    currentLabel = neighbouringLabels.Min(n => allLabels[n].GetRoot().Name);
                    Label root = allLabels[currentLabel].GetRoot();

                    foreach (var neighbor in neighbouringLabels)
                    {
                        if (root.Name != allLabels[neighbor].GetRoot().Name)
                        {
                            allLabels[neighbor].Join(allLabels[currentLabel]);
                        }
                    }
                }

                //board[currPosition.Y, currPosition.X].Label = currentLabel;
                currPosition.Label = currentLabel;

                if (i % 10000 == 0)
                    Console.WriteLine("{0}", i);
                if (i == 1130000)
                    Console.WriteLine("HERE");
            }

            // split patches into separate lists based on the label
            Dictionary<int, List<Position>> patterns = AggregatePatterns(allLabels, positions, sigmaMask);
            return patterns;

        }

        private IEnumerable<int> GetNeighbouringLabels(Position position, int patchSize)
        {
            Dictionary<int, Position> overlappingPatches = cp.GetOverlappingPatches(position, patchSize);
            var neighboringLabels = new List<int>();
            Dictionary<int, Position>.ValueCollection values = overlappingPatches.Values;
            foreach (Position pos in values)
            {
                if (pos.Label != -1)
                    neighboringLabels.Add(pos.Label);
            }

            return neighboringLabels;
        }

        private Dictionary<int, List<Position>> AggregatePatterns(Dictionary<int, Label> allLabels, List<Position> allPositions, List<int> sigmaMask)
        {
            var objects = new Dictionary<int, List<Position>>();

            for (int i = 0; i < allPositions.Count; i++)
            {
                Position pos = allPositions[i];
                if (sigmaMask[pos.Index] == 0)
                {
                    // object thresholded skip
                    continue;
                }

                int objectNumber = pos.Label;

                if (objectNumber == -1)
                    throw new Exception(String.Format("unlabelled position: {0}", pos.ToString()));

                if (objectNumber != -1)
                {
                    objectNumber = allLabels[objectNumber].GetRoot().Name;
                    
                    pos.ObjectId = objectNumber;
                    
                    if (!objects.ContainsKey(objectNumber))
                        objects[objectNumber] = new List<Position>();

                    //patterns[patternNumber].Add(new Position(new Point(j, i), Color.Black));
                    objects[objectNumber].Add(allPositions[i]);
                }

            }

            return objects;
        }

        
    }
}
