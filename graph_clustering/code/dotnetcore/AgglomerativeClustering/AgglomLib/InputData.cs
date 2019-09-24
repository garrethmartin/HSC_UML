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
    public class InputData
    {
        public List<float[]> Samples;
        //public List<int[]> SamplePositions;
        public List<float[]> NodePositions;
        public List<float[]> ClusterCentres;
        public List<int[]> NodeClusterIndex;
        public List<int[]> DatapointClusterIndex;
        public List<int[]> DatapointNodeIndex;
        public Dictionary<int, List<int>> ClusterDatapointDict;
        public Dictionary<int, List<int>> DatapointClusterIndexDict;

        public String Metric;
        public int NumPowerSpectrums;

        public String OutputFolder;

        public float Threshold;
        public int RequiredClusterCount;
        public bool UseNodes;
        public int NumDims;

        public int NumThreads;

        public int Index;
        public String TestName;
        public String TestPath;
        public String ModelPath;

        public Similarity similarity = null;
        

        public InputData(Config config)
        {
            Index = config.Int("index");
            TestName = config.Get("test_name");
            TestPath = config.Get("root_folder") + TestName + "/output_" + Index + "/";
            //ModelPath = TestPath + config.Get("model_folder") + "/";
            ModelPath = config.Get("root_folder") + config.Get("model_folder") + "/";

            NumThreads = config.Int("num_threads");

            String nodePositionFile = ModelPath + config.Get("nodePositions");
            String nodeClusterIndexFile = ModelPath + config.Get("nodeClusterIndex");
            String clusterCentresPath = ModelPath + config.Get("clusterCentres");
            String datapointClusterIndexPath = ModelPath + config.Get("datapointClusterIndex");
            String datapointNodeIndexPath = ModelPath + config.Get("datapointNodeIndex");
            String samplesPath = ModelPath + config.Get("samplesPath");
            String samplePositionsFile = ModelPath + config.Get("positionsPath");
            int numPowerSpectrums = Int32.Parse(config.Get("num_images"));
            NumPowerSpectrums = numPowerSpectrums;

            String metric = config.Get("metric").ToLower();
            Metric = metric;
            if (metric != "cosine" && metric != "euclidean" && metric != "pearson" && metric != "gradpearson" && metric != "pspearson")
            {
                throw new Exception("incorrect metric in config: " + metric);
            }
            if (metric == "cosine")
                similarity = new CosineSimilarity();
            if (metric == "euclidean")
                similarity = new EuclideanSimilarity();
            if (metric == "pearson")
                similarity = new PeasonSimilarity();
            if (metric == "gradpearson")
                similarity = new PearsonGradientSimilarity();
            if (metric == "pspearson")
            {
                //int numFeaturesForEachPS = //Int32.Parse(config.Get("numpsfeatures"));
                similarity = new PearsonAndDC(numPowerSpectrums);
            }

            OutputFolder = ModelPath + "/" + metric + "/";
            if (!Directory.Exists(OutputFolder))
                Directory.CreateDirectory(OutputFolder);

            Threshold = config.Float("threshold");
            RequiredClusterCount = config.Int("requiredClusterCount");
            UseNodes = config.Bool("useNodesNotCentroids");  // if false merges using samples proximity to centroids, if true it first identifies closest node and takes its cluster id

            if (File.Exists(datapointNodeIndexPath))
                DatapointNodeIndex = CsvParserHelper.LoadInts(datapointNodeIndexPath);

            NodePositions = CsvParserHelper.LoadFloats(nodePositionFile);
            NodeClusterIndex = CsvParserHelper.LoadDecimals(nodeClusterIndexFile);
            ClusterCentres = CsvParserHelper.LoadFloats(clusterCentresPath);

            NumDims = NodePositions[0].Length;

            if (File.Exists(datapointClusterIndexPath))
            {
                DatapointClusterIndex = CsvParserHelper.LoadDecimals(datapointClusterIndexPath);
                ClusterDatapointDict = GetClusterDatapointDictionary();
            }

            
        }

        public static Dictionary<int, float[]> GetClusterCentresAsDictionary(List<float[]> clusterCentres)
        {
            Dictionary<int, float[]> centroids = new Dictionary<int, float[]>();
            int i = 0;
            foreach (float[] centre in clusterCentres)
            {
                centroids.Add(i, centre);
                i++;
            }
            return centroids;
        }

        public Dictionary<int, List<int>> GetClusterDatapointDictionary()
        {
            var dci = new Dictionary<int, List<int>>();

            for (int i = 0; i < DatapointClusterIndex.Count; i++)
            {
                int datapointId = DatapointClusterIndex[i][0];
                int clusterId = DatapointClusterIndex[i][1];
                if (!dci.ContainsKey(clusterId))
                    dci.Add(clusterId, new List<int>());

                var datapointIndex = dci[clusterId];
                datapointIndex.Add(datapointId);
            }
            int missingCount = 0;
            for (int i = 0; i < ClusterCentres.Count + 1; i++)
            {
                if (!dci.ContainsKey(i))
                {
                    Console.WriteLine("Missing cluster? : {0}", i);
                    dci.Add(i, new List<int>());
                    missingCount++;
                }
            }

            Console.WriteLine("Missing count: {0}", missingCount);

            return dci;
        }

        public static void Test(List<int[]> datapointClusterIndex)
        {
            Dictionary<int, int> testDict = new Dictionary<int, int>();
            foreach (int[] nodeCluster in datapointClusterIndex)
            {
                int clusterKey = nodeCluster[1];
                if (testDict.ContainsKey(clusterKey))
                    testDict[clusterKey] += 1;
                else
                    testDict[clusterKey] = 1;
            }

        }
    }

}
