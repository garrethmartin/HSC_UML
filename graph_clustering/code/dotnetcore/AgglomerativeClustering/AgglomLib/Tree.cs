using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CSVParser;

namespace AgglomerativeClustering
{
    public class Tree
    {

        public static int GetRoots(BiCluster cluster, List<BiCluster> roots, float threshold, int depth = 0)
        {
            depth++;

            if (cluster.Distance < threshold)
            {
                roots.Add(cluster);
            }
            else
            {
                if (cluster.Left != null)
                    depth = GetRoots(cluster.Left, roots, threshold, depth);
                if (cluster.Right != null)
                    depth = GetRoots(cluster.Right, roots, threshold, depth);
            }
            return depth;
        }

        public static void GetLeafs(BiCluster cluster, List<int> rootIds)
        {
            if (cluster.Id > -1) // it's a leaf
            {
                rootIds.Add(cluster.Id);
                return;
            }

            if (cluster.Left != null)
                GetLeafs(cluster.Left, rootIds);
            if (cluster.Right != null)
                GetLeafs(cluster.Right, rootIds);

            return;
        }

        public static void GetLeafClusters(BiCluster cluster, List<BiCluster> leafClusters)
        {
            if (cluster.Id > -1)
            {
                leafClusters.Add(cluster);
                return;
            }
            if (cluster.Left != null)
                GetLeafClusters(cluster.Left, leafClusters);
            if (cluster.Right != null)
                GetLeafClusters(cluster.Right, leafClusters);

            return;
        }

        public static void GetClustersAsList(BiCluster cluster, List<BiCluster> clusters)
        {
            clusters.Add(cluster);

            if (cluster.Left != null) GetClustersAsList(cluster.Left, clusters);
            if (cluster.Right != null) GetClustersAsList(cluster.Right, clusters);
        }

        public static void OutputTreeData(String outputFolder, String fileName, List<BiCluster> clusters)
        {
            // output clusters
            var clusterList = new List<BiCluster>();
            Tree.GetClustersAsList(clusters[0], clusterList);
            var fileData = new List<double[]>(clusterList.Count);

            int rowLength = 4 + clusters[0].Vector.Length;

            for (int i = 0; i < clusterList.Count; i++)
            {
                BiCluster cluster = clusterList[i];
                double[] row = new double[rowLength];

                row[0] = cluster.Id;
                row[1] = cluster.Distance;
                if (cluster.Left != null)
                    row[2] = cluster.Left.Id;
                else
                    row[2] = -99999;
                if (cluster.Right != null)
                    row[3] = cluster.Right.Id;
                else
                    row[3] = -99999;

                // copy centroid to row
                for (int r = 4; r < rowLength; r++)
                {
                    row[r] = cluster.Vector[r - 4];
                }


                fileData.Add(row);
            }

            CsvParserHelper.SaveTxt(outputFolder + "/" + fileName + "_clusterList.txt", fileData);

            // output cluster, children
            fileData = new List<double[]>();
            rowLength = 5 + clusters[0].Vector.Length;
            foreach (BiCluster cluster in clusterList)
            {
                var leafClusters = new List<BiCluster>();
                Tree.GetLeafClusters(cluster, leafClusters);
                foreach (BiCluster leafCluster in leafClusters)
                {
                    double[] row = new double[rowLength];
                    row[0] = cluster.Id;
                    row[1] = cluster.Distance;
                    row[2] = leafCluster.Id;
                    if (cluster.Left != null)
                        row[3] = cluster.Left.Id;
                    else
                        row[3] = -99999;
                    if (cluster.Right != null)
                        row[4] = cluster.Right.Id;
                    else
                        row[4] = -99999;

                    // copy centroid to row
                    int vectorOffset = 5;
                    for (int r = vectorOffset; r < rowLength; r++)
                    {
                        row[r] = leafCluster.Vector[r - vectorOffset];
                    }

                    fileData.Add(row);
                }
            }

            CsvParserHelper.SaveTxt(outputFolder + "/" + fileName + "_clusterListDetail.txt", fileData);
        }


    }


    public class BiCluster
    {
        public BiCluster Parent;
        public BiCluster Left;
        public BiCluster Right;
        public float[] Vector;
        public int Id;
        public double Distance;
        public int depth;

        public BiCluster(float[] vector, BiCluster left = null, BiCluster right = null, double distance = 0.0d, int id = 0)
        {
            Vector = vector;
            Left = left;
            Right = right;
            Distance = distance;
            Id = id;
        }
    }
}
