using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using Configuration;
using CSVParser;

namespace AgglomerativeClustering
{
    class Program
    {
        static void Main(string[] args)
        {
            DateTime st = DateTime.Now;
            Console.WriteLine("Starting: {0}", st);
            var config = Config.LoadConfig(args);
            ProcessData(config);
            Console.WriteLine("Finished: {0} Duration: {1}", DateTime.Now, DateTime.Now - st);
        }

        static void ProcessData(Config config)
        {            
            var inputData = new InputData(config);

            Similarity sim = inputData.similarity;

            AgglomerativeClustering ac = new AgglomerativeClustering(inputData.NumThreads);
            List<BiCluster> clusters = null;
            if (!inputData.UseNodes)
                clusters = ac.Cluster(inputData.ClusterCentres, sim, inputData.ClusterCentres.Count);
            else
                clusters = ac.Cluster(inputData.NodePositions, sim, inputData.NodePositions.Count); 

            //Dendogram d = new Dendogram();
            //d.DrawDendogram(clusters[0], null, inputData.OutputFolder + "/all_clusters.jpg");

            Console.WriteLine("Outputting cluster list files");
            //Tree.OutputTreeData(inputData.OutputFolder, "", clusters);

            Console.WriteLine("Outputting cluster indexes");
            if (!inputData.UseNodes)
                ClusterCentreIndexFactory.CreateClusterIndexes(inputData, clusters, null);
            else
            {
                CreateClusterIndexes(inputData, clusters);
                //NodePositionsIndexFactory.CreateClusterIndexes(inputData, clusters, null);
            }
        }

        public static void CreateClusterIndexes(InputData inputData, List<BiCluster> clusters)
        {
            float threshold = inputData.Threshold;
            float decr = 0.005f; // 0.1f * threshold;

            StringBuilder results = new StringBuilder();

            while (threshold > 0.01)
            {
                List<BiCluster> roots = NodePositionsIndexFactory.SaveIndexesForThreshold(threshold, inputData, clusters, null);
            
                try
                {
                    double[] quantErrors = QuantisationError(inputData, roots);
                    Console.WriteLine(String.Format("Threshold: {0}  Num Roots: {1}  QuantErrorEuclid: {2} QuantErrorPearson: {3}", threshold, roots.Count, quantErrors[0], quantErrors[1]));
                    results.AppendLine(String.Format("{0:f3}, {1}, {2}, {3}", threshold, roots.Count, quantErrors[0], quantErrors[1]));
                    GetAvgRootCount(roots);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }

                if (roots.Count == inputData.NodePositions.Count)
                    break;

                threshold -= decr;
            }

            Console.WriteLine("*********results************");
            Console.WriteLine(results);

            using (var sw = File.CreateText(inputData.OutputFolder + "results.txt"))
            //using (StreamWriter sw = new StreamWriter(inputData.OutputFolder + "results.txt"))
            {
                sw.WriteLine(results);
            }
        }

        public static void GetAvgRootCount(List<BiCluster> roots)
        {
            List<int> rootSampleCounts = new List<int>();
            
            foreach (BiCluster cluster in roots)
            {
                int count = CountSamples(cluster, 0);
                rootSampleCounts.Add(count);
            }

            Console.WriteLine(String.Format("Total Roots: {0}  Avg Root Count: {1}  Max Branch Size: {2}", roots.Count, rootSampleCounts.Average(), rootSampleCounts.Max())); 
        }


        public static int CountSamples(BiCluster cluster, int count)
        {
            if (cluster.Left == null && cluster.Right == null)
            {
                count++;
                return count;
            }

            if (cluster.Left != null)
                count = CountSamples(cluster.Left, count);

            if (cluster.Right != null)
                count = CountSamples(cluster.Right, count);

            return count;
        }

        public static double[] QuantisationError(InputData inputData, List<BiCluster> roots)
        {
            List<float[]> nodes = inputData.NodePositions;
            int numDims = nodes[0].Length;
            List<double[]> dNodes = new List<double[]>();
            for (int i = 0; i < nodes.Count; i++)
            {
                double[] node = new double[numDims];
                for (int j = 0; j < numDims; j++)
                    node[j] = nodes[i][j];
                dNodes.Add(node);
            }

            List<double[]> centroids = new List<double[]>();
            for(int i=0; i<roots.Count;i++)
            {
                double[] centroid = new double[numDims];
                for(int j=0 ; j< numDims;j++)
                    centroid[j] = roots[i].Vector[j];
                centroids.Add(centroid);
            }

            NearestNeighbourLib.SquareEuclideanDistanceFunction distFunc = new NearestNeighbourLib.SquareEuclideanDistanceFunction();
            double euclidError = GetQuantErrorForDistFunc(inputData, centroids, dNodes, distFunc);
            NearestNeighbourLib.PearsonAndDC distFunc2 = new NearestNeighbourLib.PearsonAndDC(inputData.NumPowerSpectrums);
            double pearsonDCError = GetQuantErrorForDistFunc(inputData, centroids, dNodes, distFunc2);

            return new double[] { euclidError, pearsonDCError };
        }

        public static double GetQuantErrorForDistFunc(
            InputData inputData, List<double[]> centroids, List<double[]> samples, NearestNeighbourLib.DistanceFunctions distFunc)
        {
            NearestNeighbourLib.BruteForceNN nnMethod = new NearestNeighbourLib.BruteForceNN(centroids, distFunc);

            // get nearest indexes
            List<int[]> nearestIndexes = NearestNeighbourLib.NearestNeighbour.GetNearestNeighbours(samples, nnMethod, inputData.NumThreads);

            double error = 0.0d;
            foreach (int[] nearestIndex in nearestIndexes)
            {
                int sampleIndex = nearestIndex[0];
                int nearestCentroidIndex = nearestIndex[1];
                double dist = distFunc.Distance(centroids[nearestCentroidIndex], samples[sampleIndex]);
                error += dist;
            }
            return error;
        }
    }
}

/*
//clusters = ac.Cluster(inputData.NodePositions, psanddc_viz); //psanddc
EuclideanSimilarity es = new EuclideanSimilarity();
PeasonSimilarity ps = new PeasonSimilarity();
PearsonGradientSimilarity psg = new PearsonGradientSimilarity();
//PearsonAndDC psanddc = new PearsonAndDC(5, 3);
PearsonAndDC psanddc = new PearsonAndDC(8, 3);
//PearsonAndDC psanddc_viz = new PearsonAndDC(2, 1);
*/