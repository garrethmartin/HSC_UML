using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Ideafixxxer.CsvParser;
using Configuration;
using NearestNeighbourLib;

namespace ConnectedComponents
{
    class PatchClassifier
    {
        InputOutput io = null;

        public PatchClassifier(InputOutput io) { this.io = io; }

        public List<int[]> RunPatchClassification(String outputFolderPath, List<double[]> samples, List<double[]> nodePositions)
        {
            Stopwatch w = new Stopwatch();
            w.Start();

            
            DistanceFunctions distFunc = null;
            if (io.Metric == "fraceuclidean")
                distFunc = new FractionalEuclidean();

            if (io.Metric == "euclidean")
                distFunc = new SquareEuclideanDistanceFunction();

            if (io.Metric == "pspearson")
            {
                distFunc = new PearsonAndDC(io.NumImages);
                Console.WriteLine("Using pearson with num images: {0}", io.NumImages);
            }
            if (io.Metric == "cosine")
                distFunc = new Cosine();

            Console.WriteLine("Using distance function with brute force: {0} and numthreads: {1}", io.Metric, io.NumThreads);

            NNAlgorithm nnMethod = null;
            if (io.Metric == "euclidean")
                nnMethod = new KDTreeNN(nodePositions, distFunc);
            else
                nnMethod = new BruteForceNN(nodePositions, distFunc);

            List<int[]> nearestNeighbours = NearestNeighbour.GetNearestNeighbours(samples, nnMethod, io.NumThreads);

            w.Stop();

            long vqMS = w.ElapsedMilliseconds;
            w.Reset();

            // dont need GetDCI because each node is a cluster
            List<int[]> dciVQIndex = nearestNeighbours;
            if (!io.UseCentroids)
                dciVQIndex = MapClusters(nearestNeighbours, io.NodeToHACMapping); // /*gngHacClusterMapping*/


            w.Start();
            CsvParserHelper.SaveTxt(outputFolderPath + String.Format("/kdtree_sampleidx_hacidx_{0}.txt", io.HACIndex), dciVQIndex);
            CsvParserHelper.SaveTxt(outputFolderPath + String.Format("/kdtree_datapointClusterIndex_{0}.txt", io.HACIndex), nearestNeighbours);
            w.Stop();

            long savingMS = w.ElapsedMilliseconds;

            Console.WriteLine("VQ Time: {0} Saving Time: {1}", vqMS, savingMS);

            return dciVQIndex;
        }

        private static List<int[]> MapClusters(List<int[]> nn, Dictionary<int, int> mapping)
        {

            var newDci = new List<int[]>();

            for (int i = 0; i < nn.Count; i++)
            {
                int datapointIndex = nn[i][0];
                int clusterIndex = nn[i][1];
                int hacClusterIndex = mapping[clusterIndex];

                newDci.Add(new int[] { datapointIndex, hacClusterIndex });
            }

            return newDci;
        }
    }
}
