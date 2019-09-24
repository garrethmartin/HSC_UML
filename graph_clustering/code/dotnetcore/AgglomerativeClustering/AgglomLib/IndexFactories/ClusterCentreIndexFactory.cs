using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CSVParser;

namespace AgglomerativeClustering
{
    public class ClusterCentreIndexFactory
    {
        public static void CreateClusterIndexes(InputData inputData, List<BiCluster> clusters, List<String> labels, bool outputDendograms=false)
        {
            Console.WriteLine("{0} {1} {2}", clusters[0].Distance, clusters[0].Left.Distance, clusters[0].Right.Distance);

            float threshold = inputData.Threshold;
            float decr = 0.1f * threshold;

            while (threshold > 0.1)
            {
                
                var roots = new List<BiCluster>();
                // get nodes that are within the threshold -- top down search
                Tree.GetRoots(clusters[0], roots, threshold);
                Console.WriteLine("Threshold: {0} Number of roots: {1}", threshold, roots.Count);
                var newRootIds = new Dictionary<BiCluster, int>();


                var mapping = GetClusterIndexToParentIndexMapping(roots, newRootIds, threshold);
                List<int[]> dci = CreateDatapointClusterIndex(inputData, mapping);
                List<float[]> hacPositions = CreateAgglomerativeClusterCentres(roots);

                //String dciPath = String.Format(inputData.OutputFolder + "/datapoint_cluster_index_{0}_{1}.txt", threshold, roots.Count);
                String hacPositionsPath = String.Format(inputData.OutputFolder + "/hac_cluster_centres_{0}_{1}.txt", threshold, roots.Count);
                String gngHacMappingPath = String.Format(inputData.OutputFolder + "/gng_hac_mapping_{0}_{1}.txt", threshold, roots.Count);
                //CsvParserHelper.SaveTxt(dciPath, dci);
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

        public static Dictionary<int, int> GetClusterIndexToParentIndexMapping(List<BiCluster> roots, Dictionary<BiCluster, int> newRootIds, float threshold, int depth = 0)
        {
            var dict = new Dictionary<int, int>();

            int newHACLabel = 0;
            foreach (BiCluster root in roots)
            {
                var leafIds = new List<int>();
                Tree.GetLeafs(root, leafIds);

                int newKey = newHACLabel; // leafIds.First(x => x > -1);  // bit cacky as just chooses the first irrespective of error. prob doesn't matter as all getting the same value anyway.
                newHACLabel++;
                newRootIds.Add(root, newKey);

                foreach (int leafId in leafIds)
                {
                    if (dict.ContainsKey(leafId))
                    {
                        if (dict[leafId] != root.Id)
                            throw new Exception(String.Format("ouch: {0} {1}", leafId, root.Id));
                        continue;
                    }

                    dict.Add(leafId, newKey);
                }
            }

            return dict;
        }


        public static Dictionary<int, int> GetClusterIndexToParentIndexMapping_old(List<BiCluster> roots, Dictionary<BiCluster, int> newRootIds, float threshold, int depth = 0)
        {
            var dict = new Dictionary<int, int>();

            foreach (BiCluster root in roots)
            {
                var leafIds = new List<int>();
                Tree.GetLeafs(root, leafIds);

                int newKey = leafIds.First(x => x > -1);  // bit cacky as just chooses the first irrespective of error. prob doesn't matter as all getting the same value anyway.
                newRootIds.Add(root, newKey);

                foreach (int leafId in leafIds)
                {
                    if (dict.ContainsKey(leafId))
                    {
                        if (dict[leafId] != root.Id)
                            throw new Exception(String.Format("ouch: {0} {1}", leafId, root.Id));
                        continue;
                    }

                    dict.Add(leafId, newKey);
                }
            }

            return dict;
        }

        public static List<int[]> CreateDatapointClusterIndex(InputData inputData, Dictionary<int, int> clusterMapping)
        {
            var newDci = new List<int[]>();

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
