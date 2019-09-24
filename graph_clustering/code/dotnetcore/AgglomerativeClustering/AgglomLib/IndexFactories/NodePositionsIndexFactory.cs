using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CSVParser;

namespace AgglomerativeClustering
{
    public class NodePositionsIndexFactory
    {
        public static List<BiCluster> SaveIndexesForThreshold(float threshold, InputData inputData, List<BiCluster> clusters, List<String> labels, bool outputDendograms = false)
        {
            //Console.WriteLine("{0} {1} {2}", clusters[0].Distance, clusters[0].Left.Distance, clusters[0].Right.Distance);
            var roots = new List<BiCluster>();
            // get nodes that are within the threshold -- top down search
            Tree.GetRoots(clusters[0], roots, threshold);
            //Console.WriteLine("Threshold: {0} Number of roots: {1}", threshold, roots.Count);
            var newRootIds = new Dictionary<BiCluster, int>();

            var mapping = GetDataPointNodeIndexMapping(inputData, roots, newRootIds);
            //List<int[]> dci = CreateDatapointClusterIndex(inputData, mapping);
            List<float[]> hacPositions = CreateAgglomerativeClusterCentres(roots);

            //String dciPath = String.Format(inputData.OutputFolder + "/datapoint_cluster_index_{0:F3}_{1}.txt", threshold, roots.Count);
            String hacPositionsPath = String.Format(inputData.OutputFolder + "/hac_cluster_centres_{0:F3}_{1}.txt", threshold, roots.Count);
            String gngHacMappingPath = String.Format(inputData.OutputFolder + "/gng_hac_mapping_{0:F3}_{1}.txt", threshold, roots.Count);
            //CsvParserHelper.SaveTxt(dciPath, dci);
            CsvParserHelper.SaveTxt(hacPositionsPath, hacPositions);
            CsvParserHelper.SaveTxt(gngHacMappingPath, mapping);

            if (outputDendograms)
                DrawDendograms(inputData, roots, newRootIds, labels, threshold);

            return roots;
        }

        public static void CreateClusterIndexes(InputData inputData, List<BiCluster> clusters, List<String> labels, bool outputDendograms = false)
        {
            Console.WriteLine("{0} {1} {2}", clusters[0].Distance, clusters[0].Left.Distance, clusters[0].Right.Distance);

            float threshold = inputData.Threshold;
            float decr = 0.005f;//0.025f; // 0.1f * threshold;

            while (threshold > 0)
            {
                var roots = new List<BiCluster>();
                // get nodes that are within the threshold -- top down search
                Tree.GetRoots(clusters[0], roots, threshold);
                Console.WriteLine("Threshold: {0} Number of roots: {1}", threshold, roots.Count);
                if (roots.Count > 8000)
                {
                    Console.WriteLine("exiting as too many roots: {0}", roots.Count);
                    break;
                }
                var newRootIds = new Dictionary<BiCluster, int>();

                var mapping = GetDataPointNodeIndexMapping(inputData, roots, newRootIds);
                List<int[]> dci = CreateDatapointClusterIndex(inputData, mapping);
                List<float[]> hacPositions = CreateAgglomerativeClusterCentres(roots);

                String dciPath = String.Format(inputData.OutputFolder + "/datapoint_cluster_index_{0:F3}_{1}.txt", threshold, roots.Count);
                String hacPositionsPath = String.Format(inputData.OutputFolder + "/hac_cluster_centres_{0:F3}_{1}.txt", threshold, roots.Count);
                String gngHacMappingPath = String.Format(inputData.OutputFolder + "/gng_hac_mapping_{0:F3}_{1}.txt", threshold, roots.Count);
                if (dci.Count > 0)
                    CsvParserHelper.SaveTxt(dciPath, dci);
                CsvParserHelper.SaveTxt(hacPositionsPath, hacPositions);
                CsvParserHelper.SaveTxt(gngHacMappingPath, mapping);

                if (outputDendograms)
                    DrawDendograms(inputData, roots, newRootIds, labels, threshold);

                threshold -= decr;
            }
        }

        public static List<float[]> CreateAgglomerativeClusterCentres(List<BiCluster> roots)
        {
            var centres = new List<float[]>();

            for (int i = 0; i < roots.Count; i++)
            {
                BiCluster root = roots[i];
                centres.Add(root.Vector);
            }

            return centres;
        }


        public static Dictionary<int, int> GetDataPointNodeIndexMapping(InputData inputData, List<BiCluster> roots, Dictionary<BiCluster, int> newRootIds)
        {
            var dict = new Dictionary<int, int>();

            int newHACLabel = 0;
            foreach (BiCluster root in roots)
            {
                var nodeIds = new List<int>();
                Tree.GetLeafs(root, nodeIds);

                int newKey = newHACLabel; // nodeIds.First(x => x > -1);  // bit cacky as just chooses the first irrespective of error. prob doesn't matter as all getting the same value anyway.
                newHACLabel++;                
                newRootIds.Add(root, newKey);

                foreach (int nodeId in nodeIds)
                {
                    if (dict.ContainsKey(nodeId))
                    {
                        if (dict[nodeId] != newKey)
                            throw new Exception(String.Format("key is not the same: {0} {1} {2}", nodeId, newKey, dict[nodeId]));
                        continue;
                    }

                    dict.Add(nodeId, newKey);
                }
            }

            return dict;
        }

        public static List<int[]> CreateDatapointNodeIndex(InputData inputData, Dictionary<int, int> nodeIndexMapping)
        {
            var newDci = new List<int[]>();

            foreach (int[] row in inputData.DatapointNodeIndex)
            {
                int datapointId = row[0];
                int oldNodeId = row[1];
                int newNodeId = nodeIndexMapping[oldNodeId];

                newDci.Add(new int[] { datapointId, newNodeId });
            }

            return newDci;
        }

        public static Dictionary<int, int> GetClusterIndexToParentIndexMappingForNodePositions(InputData inputData, List<BiCluster> roots, Dictionary<BiCluster, int> newRootIds, float threshold, int depth = 0)
        {
            // this works if there are good clusters from GNG if not then we need to treat each node as a cluster

            var dict = new Dictionary<int, int>();

            foreach (BiCluster root in roots)
            {
                var nodeIds = new List<int>();
                Tree.GetLeafs(root, nodeIds);

                int newKey = nodeIds.First(x => x > -1);  // bit cacky as just chooses the first irrespective of error. prob doesn't matter as all getting the same value anyway.

                int newKeyOldClusterId = inputData.NodeClusterIndex[newKey][1];

                newRootIds.Add(root, newKey);

                foreach (int nodeId in nodeIds)
                {
                    int oldNodeClusterId = inputData.NodeClusterIndex[nodeId][1];

                    if (dict.ContainsKey(oldNodeClusterId))
                        continue;

                    dict.Add(oldNodeClusterId, newKeyOldClusterId);
                }
            }

            return dict;
        }

        public static List<int[]> CreateDatapointClusterIndex(InputData inputData, Dictionary<int, int> clusterMapping)
        {
            var newDci = new List<int[]>();
            if (inputData.DatapointClusterIndex == null)
                return newDci;

            foreach (int[] row in inputData.DatapointClusterIndex)
            {
                int datapointId = row[0];
                int oldClusterId = row[1];
                int newClusterId = clusterMapping[oldClusterId];

                newDci.Add(new int[] { datapointId, newClusterId });
            }

            return newDci;
        }

        public static void DrawDendograms(InputData inputData, List<BiCluster> roots, Dictionary<BiCluster, int> newRootIds, List<String> labels, float threshold)
        {
            String thresholdTxt = threshold.ToString().Replace('.', '_');
            Dendogram d = new Dendogram();
            for (int i = 0; i < roots.Count; i++)
            {
                BiCluster root = roots[i];
                int newKey = newRootIds[root];
                String strNewKey = newKey.ToString().Replace("-", "minus");
                String filePath = String.Format(inputData.OutputFolder + "/dendogram_{0}_{1}_{2}_rid_{3}_key_{4}.jpg", thresholdTxt, roots.Count, i, root.Id, strNewKey);
                //d.DrawDendogram(root, labels, filePath);
            }
        }


    }
}
