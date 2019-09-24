using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using GNG;
using CsvParser;


namespace GNGConsoleApp
{
    public class GNGRunner
    {
        DataTable dt;
        Graph graph;
        GrowingNeuralGas gng = null;
        InputOutputData io;
        List<int[]> info = null;
        List<double[]> quantisation_error = null;
        bool initialised = false;

        public GNGRunner(InputOutputData io)
        {
            this.io = io;
            this.dt = new DataTable(io.NumDimensions, estimatedSize: io.MaxNodes);
            this.graph = new Graph(dt, numThreads: io.NumThreads, metric: io.Metric);
            this.info = new List<int[]>();
            this.quantisation_error = new List<double[]>();
            this.gng = new GrowingNeuralGas(graph, io.Metric, io.NumDimensions, max_nodes: io.MaxNodes);
            
        }

        public void Create(List<float[]> samples)
        {

            if (io.Online)
            {
                InitGraphWithModel(io.InitMetaInfo, io.InitNodes, io.InitNodeInfo, io.InitEdges);
            }
            else
            {
                List<float[]> startPos = InitStartNodes(samples);
                if (startPos != null && startPos.Count >= 2)
                {
                    GraphNode g1 = graph.AddNode(startPos[0], 0);
                    GraphNode g2 = graph.AddNode(startPos[1], 0);
                    graph.addEdge(g1, g2);
                }
            }
            initialised = true;
        }

        public void InitGraphWithModel(List<int[]> metaInfo, List<float[]> nodes, List<double[]> nodeInfo, List<int[]> edges)
        {
            // set tlen
            int tlen = metaInfo[0][0];
            gng.tlen = tlen;

            for(int i=0;i<nodes.Count;i++)
            {
                float[] nodeData = nodes[i];
                double cumError = nodeInfo[i][0];
                int iteration = (int) nodeInfo[i][1];               

                graph.AddNode(nodeData, iteration, cumError);
            }

            for (int i=0; i<edges.Count; i++)
            {
                int[] edge = edges[i];
                int headNodeIndex = edge[0];
                int tailNodeIndex = edge[1];
                int age = edge[2];

                GraphNode headNode = graph.getNode(headNodeIndex);
                GraphNode tailNode = graph.getNode(tailNodeIndex);

                graph.addEdge(headNode, tailNode, age);             
            }
        }

        public static List<float[]> InitStartNodes(List<float[]> samples)
        {
            List<float[]> start_pos = new List<float[]>();
            float[] pos0 = new float[samples[0].Length];
            float[] pos1 = new float[samples[0].Length];
            samples[0].CopyTo(pos0, 0);
            samples[1].CopyTo(pos1, 0);
            start_pos.Add(pos0);
            start_pos.Add(pos1);

            return start_pos;
        }

        public static List<float[]> GetRandomSamples(int min, int max, int batchSize, List<float[]> samples)
        {
            var randomSamples = new List<float[]>();
            if (batchSize == -1)
                batchSize = max - min; // default to size of width

            Random r = new Random(1024);
            for (int i = 0; i < batchSize; i++)
            {
                int randomInt = r.Next(min, max);
                randomSamples.Add(samples[randomInt]);
            }

            return randomSamples;
        }

        public void Train(List<float[]> samples, int batchSize, int epoch)
        {
            if (this.initialised == false)
                Create(samples);

            Stopwatch w = new Stopwatch();

            int samples_width = samples.Count / 8;
            int j = 0;

            Console.WriteLine("Epoch: {0}  samplewidth: {1}", epoch, samples_width);

            while (j < samples.Count)
            {
                int start_idx = j;
                int end_idx = Math.Min(j + samples_width, samples.Count - 1);
                if (end_idx == start_idx)
                {
                    Console.WriteLine("start and end are equal, breaking out. start: " + start_idx + " end: " + end_idx + " total: " + samples.Count);
                    break;
                }

                Console.WriteLine("Processing start_idx: {0}  end_idx: {1}", start_idx, end_idx);

                j += samples_width;

                w.Start();
                //List<float[]> randomSamples = GetRandomSamples(start_idx, end_idx, batchSize, samples);
                List<float[]> randomSamples = GetRandomSamples(0, samples.Count-1, batchSize, samples);
                Console.WriteLine("Training with: {0} samples", randomSamples.Count);
                gng.train(randomSamples);
                w.Stop();

                int[] infoLine = OutputData(graph, epoch, w.ElapsedMilliseconds);
                info.Add(infoLine);

                w.Reset();

            }
            Console.WriteLine("**Completed samples **");

        }

        public void SaveGNGModel()
        {
            // save the GNG results
            Console.WriteLine("Saving data");

            var clusters = graph.getConnectedComponents();
            int input_dim = io.NumDimensions;
            String basePath = io.OutputPath;
            GraphHelper gh = new GraphHelper(graph, input_dim);
            Console.WriteLine("Retrieving NCI");
            int[,] nodeClusterIndex = gh.GetNodeClusterIndex(clusters);
            Console.WriteLine("Retrieving cluster centres");
            List<float[]> clusterCentres = gh.GetClusterCenters(clusters, nodeClusterIndex);
            Console.WriteLine("Retrieving node positions");
            List<float[]> codeVectors = gh.GetNodePositions();
            int[,] edgeIndex = gh.GetEdgeIndex();
            List<double[]> nodeInfoData = gh.GetNodeInfo();
            List<int[]> meta = new List<int[]>();
            meta.Add(new int[] { gng.tlen });


            String nodeClusterIndexPath = basePath + "/node_cluster_index_.txt";
            String clusterCentresPath = basePath + "/cluster_centeres.txt";
            String codeVectorsPath = basePath + "/node_position_list.txt";
            String nodeInfo = basePath + "/node_info.txt";

            Console.WriteLine("saving files");
            CsvParserHelper.SaveTxt(clusterCentresPath, clusterCentres);
            CsvParserHelper.SaveTxt(codeVectorsPath, codeVectors, colDelimiter: ',');
            CsvParserHelper.SaveTxt(basePath + "/edge_index.txt", edgeIndex, 3, ',');
            InputOutputData.SaveTxt(nodeClusterIndexPath, nodeClusterIndex, 2, ',');
            CsvParserHelper.SaveTxt(basePath + "/node_info.txt", nodeInfoData, ',');
            CsvParserHelper.SaveTxt(basePath + "/meta.txt", meta, ',');

        }

        public void SaveLog()
        {
            if (io.OutputToLog)
            {
                InputOutputData.OutputLog(info, quantisation_error);
            }
        }
        private static int[] OutputData(Graph g, int epoch, long elapsedTime)
        {
            List<List<GraphNode>> connectedComps = g.getConnectedComponents();

            int[] infoLine = GetInfoLine(g.getNodeCount(), g.getEdgeCount(), connectedComps.Count, epoch, elapsedTime);

            Console.WriteLine("training: {0}  nodes: {1} edges: {2} connected components: {3}  duration: {4}",
                epoch, infoLine[1], infoLine[2], infoLine[3], infoLine[4]);

            // print connected component stats
            StringBuilder sb = new StringBuilder(" ");
            int lessThan = 0;
            for (int c = 0; c < connectedComps.Count; c++)
            {
                if (connectedComps[c].Count < 60)
                    lessThan++;
                else
                {
                    sb.Append(connectedComps[c].Count);
                    sb.Append(" ");
                }
            }
            Console.WriteLine("Cluster counts <60: {0} >60: {1}", lessThan, sb);
            Console.WriteLine(DateTime.Now);

            return infoLine;
        }
        private static int[] GetInfoLine(int nodeCount, int edgeCount, int numConnComps, int epoch, long elapsedTime)
        {
            int[] infoLine = new int[5];
            infoLine[0] = epoch;
            infoLine[1] = nodeCount;
            infoLine[2] = edgeCount;
            infoLine[3] = numConnComps;
            infoLine[4] = (int)elapsedTime;
            return infoLine;
        }
    }
}
