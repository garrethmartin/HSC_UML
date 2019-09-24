using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Drawing;
using Configuration;
using Ideafixxxer.CsvParser;
using SampleHandlerLib;

namespace ConnectedComponents
{
    class Program
    {

        public static void Main(string[] args)
        {
 
            var config = Config.LoadConfig(args);

            InputOutput io = new InputOutput(config);

            List<int[]> completeSparseCounts = new List<int[]>();
            List<String> completeCatalogue = new List<String>();

            int maxHACClusterId = -1;

            // load the sky areas 
            List<SkyArea> skyAreas = io.LoadSkyAreas(io.Index, io.RootFolderPath + io.SkyAreasFileName, true);
            foreach(SkyArea skyArea in skyAreas)
            {
                String skyAreaRootFolderPath = io.TestBasePath +"/" + skyArea.Id + "/";
                String samplesFilePath = io.TestBasePath + skyArea.Id + "/" + io.SamplesFileName;
                // Get the patch classifications for this skyarea

                List<double[]> samples = CsvParserHelper.LoadDoubles(skyAreaRootFolderPath + io.SamplesFileName);                
                List<double[]> nodePositions = null;
                if (io.UseCentroids)
                    nodePositions = CsvParserHelper.LoadDoubles(io.ModelFolderPath + io.AgglomFolderName + "/" + io.HACCentresFileName);
                else
                    nodePositions = CsvParserHelper.LoadDoubles(io.ModelFolderPath + io.NodePositionsFileName);
                List<double[]> normedSamples = samples;
                if (io.LogAllSamples)
                {
                    normedSamples = SampleHandlerLib.Normalize.LogDoubles(samples);
                    normedSamples = SampleHandlerLib.Normalize.NormalizeData(samples, io.Mu, io.Std);
                }
                PatchClassifier pc = new PatchClassifier(io);
                List<int[]> dHacCI = pc.RunPatchClassification(skyAreaRootFolderPath, samples, nodePositions);
                for(int i=0;i<dHacCI.Count;i++)
                {
                    if (dHacCI[i][1] > maxHACClusterId)
                        maxHACClusterId = dHacCI[i][1];
                }

                // run blob detection and output features
                List<int[]> sparseCounts = RunConnComps(skyArea, config, io, dHacCI, skyAreaRootFolderPath, completeSparseCounts, completeCatalogue);
                Console.WriteLine(String.Format("Finished skyarea: {0}", skyArea.Id));
            }

            CsvParserHelper.SaveTxt(io.ModelFolderPath + String.Format("/complete_sparse_counts_{0}.txt", io.TestName), completeSparseCounts, colDelimiter: ',');
            CsvParserHelper.SaveTxt(io.ModelFolderPath + String.Format("/complete_object_catalogue_{0}.txt", io.TestName), completeCatalogue);
        }

        static void AddSparseCounts(List<int[]> completeSparseCounts, List<int[]> skyAreaSparseCounts, SkyArea skyArea)
        {
            foreach(int[] sparseCount in skyAreaSparseCounts)
            {
                int[] newSC = new int[sparseCount.Length + 2];
                newSC[0] = skyArea.Index;
                newSC[1] = skyArea.Id;
                for (int i = 0; i < sparseCount.Length; i++)
                    newSC[i + 2] = sparseCount[i];
                completeSparseCounts.Add(newSC);
            }

        }

        static void AddCatalogueRows(List<String> completeCatalogue, List<String> skyAreaCatalogue, SkyArea skyArea)
        {
            foreach(String line in skyAreaCatalogue)
            {
                String newLine = String.Format("{0} {1} {2}", skyArea.Index, skyArea.Id, line);
                completeCatalogue.Add(newLine);
            }
        }

        static List<int[]> RunConnComps(
            SkyArea skyArea, 
            Config config, 
            InputOutput io, 
            List<int[]> dHacCI, 
            String skyAreaPath, 
            List<int[]> completeSparseCounts, 
            List<String> completeCatalogue)
        {

            String positions_file_path = skyAreaPath + io.PositionsFileName; // config.Get("positions_file");
            //String datapoint_cluster_index_file_path = config.Get("datapoint_cluster_index_file");
            //String datapoint_hac_cluster_index_file_path = config.Get("datapoint_hac_cluster_index_file");
            //String color_file_path = config.Get("color_file_path");
            String outputPath = io.ModelFolderPath + "/conncomps/"; //skyAreaPath; // config.Get("output_path");
            if (!Directory.Exists(outputPath))
                Directory.CreateDirectory(outputPath);
            int imageWidth = 1; // config.Int("image_width");
            int imageHeight = 1; // config.Int("image_height");
            //int minBlobDistance = config.Int("min_blob_distance");
            bool saveSlices = config.Bool("save_slices"); // false;
            int patchSize = config.Int("patch_size"); // 1;
            int maxDistance = (patchSize * 2) + 1;
            //int[] sigmas = config.Ints("sigmas");
            String[] sigmaFilePaths = config.Strings("sigma_file_paths");
            int minSize = config.Int("min_object_size_in_patches");

            Stopwatch sw = new Stopwatch();
            sw.Start();
            List<int[]> positions = CsvParserHelper.LoadInts(positions_file_path);
            //List<int[]> dci = CsvParserHelper.LoadInts(datapoint_cluster_index_file_path);
            //List<int[]> dHacCI = CsvParserHelper.LoadInts(datapoint_hac_cluster_index_file_path);
            //List<float[]> colorFile = CsvParserHelper.LoadFloats(color_file_path);
            sw.Stop();
            long fileLoading = sw.ElapsedMilliseconds;

            sw.Reset();
            sw.Start();
            //List<Position> posObjsX = ConvertPositions(positions, dci, dHacCI);
            List<Position> posObjsX = ConvertPositions(positions, dHacCI);
            PositionComparerX cpX = new PositionComparerX();
            posObjsX.Sort(cpX);

            sw.Stop();
            long sorting = sw.ElapsedMilliseconds;

            Dictionary<int, int> clusterSizes = GetClusterSizes(posObjsX);
            List<int[]> clusterSizeList = OrderAndConvertToList(clusterSizes);
            //CsvParserHelper.SaveTxt(outputPath + "/clusterSizeList.txt", clusterSizeList, colDelimiter: ',');
            int maxClusterId = io.MaxClusterId; //GetMaxClusterId(clusterSizeList) + 1;

            sw.Reset();
            
            // load the masks
            String[] sigma_mask_file_paths = config.Strings("sigma_file_paths");
            var sigmaMasks = new Dictionary<string, List<int>>();
            foreach (String sigma_file_path in sigma_mask_file_paths)
            {
                List<int[]> sigmaMask = CsvParserHelper.LoadInts(skyAreaPath + sigma_file_path);
                List<int> tempMask = new List<int>();
                for (int i = 0; i < sigmaMask.Count; i++)
                    tempMask.Add(sigmaMask[i][0]);
                sigmaMasks.Add(sigma_file_path, tempMask);
            }

            // run find process for each wavelength
            var multiLevelObjects = new List<Dictionary<int, List<Position>>>();
            foreach(String sigmaFile in sigmaMasks.Keys)
            {
                sw.Reset();
                sw.Start();
                Console.WriteLine("{0}", sigmaFile);
                List<int> sigmaMask = sigmaMasks[sigmaFile];
                
                ClosestPatches cp = new ClosestPatches(posObjsX, sigmaMask, cpX, patchSize, maxDistance);
                ConnCompsAlgorithm cc = new ConnCompsAlgorithm(cp);
                Dictionary<int, List<Position>> levelObjects = cc.Find(posObjsX, sigmaMask, patchSize);

                // reset labels
                for (int i = 0; i < posObjsX.Count; i++)
                {
                    posObjsX[i].Label = -1;
                    posObjsX[i].ObjectId = -1;
                }

                sw.Stop();
                Console.WriteLine("Object Searching: {0} num objects: {1} duration: {2} ms", sigmaFile, levelObjects.Count, sw.ElapsedMilliseconds);
                multiLevelObjects.Add(levelObjects);
            }


            // combine object lists by looking for overlaps
            Dictionary<int, List<Position>> objects = CreateMultiLevelMaskMap(imageHeight, imageWidth, multiLevelObjects);

            // the rest is the same
            // save the feature matrix. One row for each object. Each column is a count of patches of each label.
            List<int[]> sparseCounts = SaveObjectSamples(outputPath, objects, maxClusterId, minSize);
            CsvParserHelper.SaveTxt(outputPath + String.Format("/object_counts_{0}_{1}_{2}_{3}_{4}.txt", io.HACIndex, io.Metric, io.TestName, io.Index, skyArea.Id), sparseCounts, ',');
            //CsvParserHelper.SaveTxt(outputPath + "/datapoint_object_index.txt", CreateObjectMapping(objects));

            //Dictionary<int, Color> colourDict = CreateActiveColourDict(posObjsX, colorFile);
            //SaveObjectImages(outputPath, posObjsX, objects, colourDict, patchSize, saveSlices, minSize);

            // create catalogue
            List<String> catalogue = CreateObjectCatalogue(outputPath, posObjsX, objects, patchSize, minSize);
            CsvParserHelper.SaveTxt(outputPath + String.Format("object_catalogue_{0}_{1}_{2}_{3}_{4}.txt", io.HACIndex, io.Metric, io.TestName, io.Index, skyArea.Id), catalogue);

            // create ds9 region file
            List<String> ds9RegionFile = CreateDS9RegionFile(posObjsX, objects, patchSize, minSize);
            CsvParserHelper.SaveTxt(outputPath + String.Format("ds9_region_{0}_{1}_{2}_{3}_{4}.reg", io.HACIndex, io.Metric, io.TestName, io.Index, skyArea.Id), ds9RegionFile);

            // save complete image of all found objects
            // Bitmap image = CreateWholeImage(objects, imageWidth, imageHeight, patchSize, minSize, posObjsX);
            // image.Save(outputPath + String.Format("/image_{0}_{1}_{2}_{3}_{4}.png", io.HACIndex, io.Metric, io.TestName, io.Index, skyArea.Id));

            AddSparseCounts(completeSparseCounts, sparseCounts, skyArea);
            AddCatalogueRows(completeCatalogue, catalogue, skyArea);

            return sparseCounts;
        }


        static Dictionary<int, List<Position>> CreateMultiLevelMaskMap(int height, int width, List<Dictionary<int, List<Position>>> objects)
        {
            // assumes objects is ordered by highest threshold first arrghh

            Dictionary<int, List<Position>> newObjectList = new Dictionary<int, List<Position>>();

            var matrix = new SparseMatrix<int>();

            //var matrix = new int[height, width];
            
            int objectId = 1;
            foreach (Dictionary<int, List<Position>> levelObjects in objects)
            {
                Console.WriteLine("Recalculating objects num objects in this level: {0}", levelObjects.Count);
                foreach (List<Position> objectPatches in levelObjects.Values)
                {
                    if (objectPatches.Count == 1)
                        continue; // skip single pixel objects

                    // write object to map
                    int i = 0;
                    for (; i < objectPatches.Count; i++)
                    {
                        Position position = objectPatches[i];

                        int x = position.X;
                        int y = position.Y;

                        if (matrix[y, x] == 0)
                            matrix[y, x] = objectId;
                        else
                            // overlapping object
                            break;
                    }

                    if (i < objectPatches.Count)
                    {
                        // overlap so undo writing
                        for (int j = 0; j < i; j++)
                        {
                            Position position = objectPatches[j];

                            int x = position.X;
                            int y = position.Y;

                            if (matrix[y, x] == objectId)
                                matrix[y, x] = 0;
                            else
                                Console.WriteLine("Shouldn't happen");
                        }
                        continue; // don't increment objectId as skipping object because it overlaps
                    }

                    // good object, no overlaps.
                    newObjectList.Add(objectId, objectPatches);
                    objectId++;
                }
            }

            return newObjectList;
        }


        public static Rectangle FindObjectDimensions(List<Position> objectPatches, int patchSize)
        {
            int minX = objectPatches.Min(p => p.X) - patchSize;
            int maxX = objectPatches.Max(p => p.X) + patchSize;

            int minY = objectPatches.Min(p => p.Y) - patchSize;
            int maxY = objectPatches.Max(p => p.Y) + patchSize;

            int width = maxX + 1 - minX;
            int height = maxY + 1 - minY;

            return new Rectangle(minX, minY, width, height);
        }


        public static List<int[]> SaveObjectSamples(String filePath, Dictionary<int, List<Position>> objects, int maxClusterId, int minSize=40)
        {
            int numClusterIds = maxClusterId;

            //int[] sparsityCount = new int[numClusterIds];

            List<int[]> sparseCounts = new List<int[]>();
            Dictionary<int, List<Position>>.KeyCollection keys = objects.Keys;
            int objId = 0;
            foreach(int key in keys)
            {
                int[] objectCounts = new int[numClusterIds+1];
                objectCounts[0] = objId++;
                List<Position> objectPositions = objects[key];
                if (objectPositions.Count < minSize)
                    continue;
                foreach (Position pos in objectPositions)
                {                    
                    objectCounts[pos.HACCluster+1] += 1;
                    //sparsityCount[pos.HACCluster] += 1;
                }
                sparseCounts.Add(objectCounts);
            }

            
            
            return sparseCounts;

            /*
            int[] sparsityMapper = new int[numClusterIds];
            int newIndex = 0;
            for (int i = 0; i < numClusterIds; i++)
            {
                if (sparsityCount[i] > 0)
                {
                    sparsityMapper[i] = newIndex;
                    newIndex++; // only increment if there are values to create dense mapping.
                }
            }

            int denseNumClusterIds = newIndex;
            List<int[]> denseCounts = new List<int[]>();
            int objid = 0;
            foreach (int[] objectCount in sparseCounts)
            {
                int[] denseCount = new int[denseNumClusterIds+1];
                denseCount[0] = objid;

                for (int i = 0; i < numClusterIds; i++)
                {
                    if (objectCount[i] > 0)
                    {
                        int denseIndex = sparsityMapper[i];
                        denseCount[denseIndex+1] = objectCount[i];
                    }
                }

                denseCounts.Add(denseCount);
                objid++;
            }

            CsvParserHelper.SaveTxt(filePath + "/dense_counts.txt", denseCounts, ',');
            CsvParserHelper.SaveTxt(filePath + "/dense_sparse_mapper.txt", sparsityMapper);
            //CsvParserHelper.SaveTxt(filePath + "/sparse_counts.txt", sparseCounts, ',');
             */
        }


        public static List<int[]> CreateObjectMapping(Dictionary<int, List<Position>> objects)
        {
            Dictionary<int, List<Position>>.ValueCollection objectPatchLists = objects.Values;

            int numPositions = objectPatchLists.Sum((a) => a.Count);

            var objectMapping = new List<int[]>();
            for (int i = 0; i < numPositions; i++)
                objectMapping.Add(new int[] { i, -1 });

            foreach (List<Position> objectPatches in objectPatchLists)
            {
                objectPatches.ForEach((pos) => objectMapping[pos.Index][1] = pos.ObjectId);
            }

            if (objectMapping.TrueForAll(a => a[1] > -1) == false)
                throw new Exception("not all positions have been updated");
            
            return objectMapping;

        }

        public static void Test(ClosestPatches cp, List<Position> posObjsX, int patchSize)
        {
            int count = 0;
            for (int i = 0; i < posObjsX.Count; i++)
            {
                Position tPos = posObjsX[i];

                Dictionary<int, Position> overlappingPatches = cp.GetOverlappingPatches(tPos, patchSize);
                if (i % 1000 == 0)
                    Console.WriteLine("{0} {1}", i, count);
                count += overlappingPatches.Count;
            }
        }

        public static Dictionary<int, int> GetClusterSizes(List<Position> positions)
        {
            Dictionary<int, int> sizes = new Dictionary<int, int>();
            for (int i = 0; i < positions.Count; i++)
            {
                Position pos = positions[i];
                int hac = pos.HACCluster;
                if (!sizes.ContainsKey(hac))
                    sizes.Add(hac, 0);

                sizes[hac] += 1;
            }

            return sizes;
        }

        public static List<int[]> GetReducedHACClusterList(int[,] hacProximityCounts, List<int[]> clusterSizeList, int maxClusterId)
        {
            List<int[]> list = new List<int[]>();
            int numClusters = clusterSizeList.Count;

            for (int i = 0; i < numClusters; i++)
            {
                int rowClusterId = clusterSizeList[i][0];

                int[] n = new int[numClusters + 1];
                n[0] = rowClusterId;
                for (int j = 0; j < numClusters; j++)
                {
                    int colClusterId = clusterSizeList[j][0];
                    int count = hacProximityCounts[rowClusterId, colClusterId];
                    n[j+1] = count;
                }

                list.Add(n);
            }

            return list;
        }

        public static List<int[]> OrderAndConvertToList(Dictionary<int, int> dict)
        {
            
            //var ordered = dict.OrderBy(x => x.Value);
            Dictionary<int, int>.KeyCollection keys = dict.Keys;
            var list = new List<int[]>();
            foreach (int key in keys)
            {
                list.Add(new int[] { key, dict[key]});
            }

            return list;
        }

        public static int GetMaxClusterId(List<int[]> clusters)
        {
            int max = -1;

            for (int i = 0; i < clusters.Count; i++)
            {
                if (clusters[i][0] > max)
                    max = clusters[i][0];
            }
            return max;

        }


        public static List<Position> ConvertPositions(List<int[]> positions, List<int[]> dHacCI)
        {
            var posObjs = new List<Position>();

            for (int index = 0; index < positions.Count; index++)
            {
                Position p = new Position(index, positions[index]);
                p.HACCluster = dHacCI[index][1];
                posObjs.Add(p);
            }

            return posObjs;
        }

        public static List<Position> ConvertPositions(List<int[]> positions, List<int[]> dci, List<int[]> dHacCI)
        {
            var posObjs = new List<Position>();

            if (dci.Count != positions.Count || dHacCI.Count != positions.Count)
                throw new Exception("counts are different");            

            for (int index = 0; index < positions.Count; index++)
            {
                Position p = new Position(index, positions[index]);
                p.HACCluster = dHacCI[index][1];
                p.GNGCluster = dci[index][1];
                posObjs.Add(p);
                //posObjs.Add(new Position(i, positions[i]));
            }

            return posObjs;
        }

        private static Color GetRandColor()
        {
            Random rand = new Random();
            int max = byte.MaxValue + 1; // 256
            int r = rand.Next(max);
            int g = rand.Next(max);
            int b = rand.Next(max);
            Color c = Color.FromArgb(r, g, b);
            return c;
        }
	
	/*
        private static Bitmap CreateWholeImage(Dictionary<int, List<Position>> objects, int width, int height, int patchSize, int minSize, List<Position> positions)
        {
            int minY = int.MaxValue;
            int minX = int.MaxValue;
            int maxX = 0;
            int maxY = 0;
            foreach(Position pos in positions)
            {
                if (pos.Y < minY)
                    minY = pos.Y;
                if (pos.X < minX)
                    minX = pos.X;
                if (pos.X > maxX)
                    maxX = pos.X;
                if (pos.Y > maxY)
                    maxY = pos.Y;
            }
            

            int height_offset = positions.Min(p => p.Y);
            int width_offset = positions.Min(p => p.X);
            height = positions.Max(p => p.Y) - height_offset + 1;
            width = positions.Max(p => p.X) - width_offset + 1;
            Console.WriteLine("hoff: {0} woff:{1} h:{2} w:{3}", height_offset, width_offset, height, width);
            height_offset = minY - patchSize;
            width_offset = minX - patchSize;
            height = maxY - height_offset + patchSize;
            width = maxX - width_offset + patchSize;
            Console.WriteLine("hoff: {0} woff:{1} h:{2} w:{3}", height_offset, width_offset, height, width);
            var bmp = new Bitmap(width+1, height+1);
            int count = 0;
            
            //KnownColor[] names = (KnownColor[])Enum.GetValues(typeof(KnownColor));
            Dictionary<int, List<Position>>.ValueCollection objectPatchLists = objects.Values;
            //int prevRand = 0;
            Random randomGen = new Random();
            foreach (List<Position> objectPatches in objectPatchLists)
            {
                if (objectPatches.Count < minSize) 
                    continue;
                
                //int rand = prevRand;
                //while (rand == prevRand)
                //    rand = randomGen.Next(names.Length);
                //prevRand = rand;
                //KnownColor randomColorName = names[rand];
                //Color randomColor = Color.FromKnownColor(randomColorName);
                Color randomColor = GetRandColor();
                
                count++;
                foreach (Position position in objectPatches)
                {
                    int left = position.X - patchSize;
                    int right = position.X + patchSize;
                    int top = position.Y + patchSize;
                    int bottom = position.Y - patchSize;

                    for (int x = left; x < right; x++)
                    {
                        for (int y = bottom; y < top; y++)
                        {
                            try
                            {
                                bmp.SetPixel(x - width_offset, height - (y - height_offset), randomColor);//shift position by minX and minY
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine(ex.ToString());
                                Console.WriteLine(ex.Source);
                                Console.WriteLine(ex.Message);
                                Console.WriteLine(ex.InnerException);
                                Console.WriteLine("x {0} y{1} h offset: {2} w offset: {3}  h: {4}", x, y, height_offset, width_offset, height);
                                throw new Exception(String.Format("x {0} y{1} h offset: {2} w offset: {3}  h: {4}", x, y, height_offset, width_offset, height), ex);
                            }
                        }
                    }
                }
            }
            Console.WriteLine("Wrote {0} objects to the Whole Image", count);

            return bmp;
        }
	*/

        private static Dictionary<int, Color> CreateActiveColourDict(List<Position> objectPatches, List<float[]> colourFile)
        {
            // create colour dictionary from list
            Dictionary<int, Color> colorDict = new Dictionary<int, Color>();

            foreach (float[] colourRow in colourFile)
            {
                // 1,2855,2855,0,0,255,240,0
                int red = (int) colourRow[2];
                int green = (int) colourRow[3];
                int blue = (int) colourRow[4];

                int hacClusterId = (int) colourRow[0];

                colorDict.Add(hacClusterId, Color.FromArgb(red, green, blue));
            }

            for (int i = 0; i < objectPatches.Count; i++)
            {
                int clusterId = objectPatches[i].HACCluster;
                //int index = objectPatches[i].Index;
                if (!colorDict.ContainsKey(clusterId))
                {
                    Console.WriteLine("error {0} doesn't exist", clusterId);
                    colorDict.Add(clusterId, Color.FromArgb(255, 0, 255)); // purple                        
                }

            }
            return colorDict;
        }


        private static Dictionary<int, Color> CreateColourDict(List<Position> objectPatches, List<float[]> colourFile)
        {
            // create colour dictionary from list
            Dictionary<int, Color> colorDict = new Dictionary<int, Color>();
            for (int i=0; i<objectPatches.Count;i++)
            {
                int clusterId = objectPatches[i].HACCluster;
                //int index = objectPatches[i].Index;
                if (!colorDict.ContainsKey(clusterId))
                {
                    int temp_color_idx = clusterId;
                    while(temp_color_idx >= colourFile.Count)
                    {
                        temp_color_idx = temp_color_idx - colourFile.Count;                        
                    }
                    if (temp_color_idx < 0) temp_color_idx = 0;

                    int red = (int) (colourFile[temp_color_idx][0] * 255);
                    int green = (int) (colourFile[temp_color_idx][1] * 255);
                    int blue = (int) (colourFile[temp_color_idx][2] * 255);

                    colorDict.Add(objectPatches[i].HACCluster, Color.FromArgb(red, green, blue));
                }
            }
            return colorDict;
        }


        private static List<String> CreateObjectCatalogue(String outputPath, List<Position> allPatches, Dictionary<int, List<Position>> objects, int patchSize, int minSize = 40)
        {
            var rows = new List<string>();

            Dictionary<int, List<Position>>.ValueCollection objectPatchLists = objects.Values;
            int count = 0;

            IEnumerable<KeyValuePair<int, int>> clusterSizeList = GetClusterSizeList(allPatches);

            foreach (List<Position> objectPatches in objectPatchLists)
            {
                if (objectPatches.Count < minSize)
                {
                    count++;
                    continue;
                }

                // positions and average centre
                Rectangle boundingRect = GetObjectRectangle(objectPatches, patchSize, true);
                Point centre = GetObjectCentre(objectPatches);
                Rectangle cutout = GetObjectCutOutRectangle(boundingRect, centre);

                // objid numpatches width height cleft cright ctop cbottom cx cy bleft bright btop bbottom
                String row = String.Format("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}",
                    count, objectPatches.Count, boundingRect.Width, boundingRect.Height, 
                    cutout.Left, cutout.Right, cutout.Top, cutout.Bottom, centre.X, centre.Y,
                    boundingRect.Left, boundingRect.Right, boundingRect.Top, boundingRect.Bottom); 

                rows.Add(row);
                count++;
            }

            return rows;
        }

        private static List<String> CreateDS9RegionFile(List<Position> allPatches, Dictionary<int, List<Position>> objects, int patchSize, int minSize = 40)
        {
            var rows = new List<string>();

            Dictionary<int, List<Position>>.KeyCollection objectKeys = objects.Keys;

            //Dictionary<int, List<Position>>.ValueCollection objectPatchLists = objects.Values;
            int count = 0;

            IEnumerable<KeyValuePair<int, int>> clusterSizeList = GetClusterSizeList(allPatches);

            rows.Add("image"); // pixel coords

            foreach (int key in objectKeys)
            {
                List<Position> objectPatches = objects[key];

                if (objectPatches.Count < minSize)
                {
                    count++;
                    continue;
                }

                // positions and average centre
                Rectangle boundingRect = GetObjectRectangle(objectPatches, patchSize, true);
                Point centre = GetObjectCentre(objectPatches);
                Rectangle cutout = GetObjectCutOutRectangle(boundingRect, centre);
                String sizeArcSec = "25";
                String row = String.Format("circle({0}, {1}, {2}) # text={{{3}}} color=cyan",
                    centre.X, centre.Y, sizeArcSec, key);

                rows.Add(row);
                count++;
            }

            return rows;
        }

        private static Rectangle GetObjectCutOutRectangle(Rectangle boundingRect, Point centre)
        {
            int centreX = boundingRect.X + (boundingRect.Width / 2);
            int centreY = boundingRect.Y + (boundingRect.Height / 2);

            int offsetX = centreX - centre.X;
            int offsetY = centreY - centre.Y;

            // move bounding rect
            int newX = boundingRect.X - offsetX;
            int newY = boundingRect.Y - offsetY;
            boundingRect.Location = new Point(newX, newY);

            return boundingRect;
        }

        /*
         * CENTRE OF MASS   http://stackoverflow.com/questions/12801400/find-the-center-of-mass-of-points
         for each point n
        {
            totalmass += n.mass   (could use strength instead)
            totalx += n.x*n.mass
            totaly += n.y*n.mass
        }
        center = (totalx/totalmass,totaly/totalmass)
         */

        private static void SaveObjectImages(String outputPath, List<Position> allPatches, Dictionary<int, List<Position>> objects, 
            Dictionary<int,Color> colourDict, int patchSize, bool outputSlices, int minSize)
        {
            Dictionary<int, List<Position>>.ValueCollection objectPatchLists = objects.Values;
            int count = 0;
            int saveCount = 0;
            IEnumerable<KeyValuePair<int, int>> clusterSizeList = GetClusterSizeList(allPatches);

            foreach (List<Position> objectPatches in objectPatchLists)
            {
                if (objectPatches.Count < (minSize+30))
                {
                    count++;
                    continue;
                }

                //var colourDict = CreateColourDict(objectPatches, colourFile);
                Bitmap objectImage = CreateObjectBitmap(objectPatches, clusterSizeList, colourDict, patchSize);
                String objectImagePath = String.Format("{0}/object_{1}_{2}.png", outputPath, count, objectPatches.Count);
                objectImage.Save(objectImagePath);
                objectImage.Dispose();
                objectImage = null;
                saveCount++;

                //
                if (outputSlices)
                {
                    String objectSliceDirectoryPath = outputPath + String.Format("/object_{0}", count);
                    if (!Directory.Exists(objectSliceDirectoryPath))
                        Directory.CreateDirectory(objectSliceDirectoryPath);

                    int sliceCount = 0;
                    foreach (KeyValuePair<int, int> kvp in clusterSizeList)
                    {
                        int clusterId = kvp.Key;
                        int patchCount = 0;
                        foreach (Position pos in objectPatches)
                        {
                            if (pos.HACCluster == clusterId)
                                patchCount++;
                        }

                        if (patchCount < 4)
                            continue;

                        Bitmap objectSlice = CreateObjectSliceBitmap(objectPatches, colourDict, clusterId, patchSize);
                        objectImagePath = String.Format("{0}/object_{1}_slice_{2}_{3}_patchcount_{4}_clustid_{5}.png", objectSliceDirectoryPath, count, sliceCount, objectPatches.Count, patchCount, clusterId);
                        objectSlice.Save(objectImagePath);

                        sliceCount++;
                        if (sliceCount > 40)
                            break;
                    }
                }
                count++;
            }
            Console.WriteLine("Saved {0} minsize(patches) {1} objects less than min: {2}  Total: {3}", saveCount, minSize, count, saveCount + count);
        }

        private static Rectangle GetObjectRectangle(List<Position> objectPatches, int patchSize, bool makeSquare = false)
        {
            int minX = objectPatches.Min(p => p.X) - patchSize;
            int maxX = objectPatches.Max(p => p.X) + patchSize;

            int minY = objectPatches.Min(p => p.Y) - patchSize;
            int maxY = objectPatches.Max(p => p.Y) + patchSize;

            int width = maxX + 1 - minX;
            int height = maxY + 1 - minY;

            if (makeSquare)
            {
                if (width > height)
                {
                    int diff = width - height;
                    int halfdiff = diff / 2;

                    minY = minY - halfdiff;
                    maxY = maxY + halfdiff;

                    if (halfdiff * 2 < diff)
                        maxY += 1;
                    if (halfdiff * 2 > diff)
                        maxY -= 1;

                    width = maxX + 1 - minX;
                    height = maxY + 1 - minY;
                    if (width != height)
                        Console.WriteLine("Error");
                }

                if (height > width)
                {
                    int diff = height - width;
                    int halfdiff = diff / 2;
                    minX = minX - halfdiff;
                    maxX = maxX + halfdiff;

                    if (halfdiff * 2 < diff)
                        maxX += 1;
                    if (halfdiff * 2 > diff)
                        maxX -= 1;

                    width = maxX + 1 - minX;
                    height = maxY + 1 - minY;

                    if (width != height)
                        Console.WriteLine("Error");
                }
            }

            Rectangle r = new Rectangle(minX, minY, width, height);
            
            return r;
        }

        private static Point GetObjectCentre(List<Position> objectPatches)
        {
            double avgX = objectPatches.Average(p => p.X);
            double avgY = objectPatches.Average(p => p.Y);

            return new Point((int) avgX, (int) avgY);
        }


        private static Bitmap CreateObjectBitmap(List<Position> objectPatches, IEnumerable<KeyValuePair<int, int>> clusterSizeList, Dictionary<int, Color> colorDict, int patchSize)
        {

            int minX = objectPatches.Min(p => p.X) - patchSize;
            int maxX = objectPatches.Max(p => p.X) + patchSize;

            int minY = objectPatches.Min(p => p.Y) - patchSize;
            int maxY = objectPatches.Max(p => p.Y) + patchSize;

            int width = maxX + 1 - minX;
            int height = maxY + 1 - minY;

            var bmp = new Bitmap(width, height);

            foreach (Position position in objectPatches)
            {
                int left = position.X - patchSize;
                int right = position.X + patchSize;
                int top = position.Y + patchSize;
                int bottom = position.Y - patchSize;

                Color patchColour = colorDict[position.HACCluster];

                for (int x = left; x < right; x++)
                {
                    for (int y = bottom; y < top; y++)
                        bmp.SetPixel(x - minX, y - minY, patchColour);//shift position by minX and minY
                }

            }

            return bmp;
        }

        private static Bitmap CreateObjectBitmapOld(List<Position> objectPatches, IEnumerable<KeyValuePair<int, int>> clusterSizeList, Dictionary<int, Color> colorDict, int patchSize)
        {

            int minX = objectPatches.Min(p => p.X) - patchSize;
            int maxX = objectPatches.Max(p => p.X) + patchSize;

            int minY = objectPatches.Min(p => p.Y) - patchSize;
            int maxY = objectPatches.Max(p => p.Y) + patchSize;

            int width = maxX + 1 - minX;
            int height = maxY + 1 - minY;

            var bmp = new Bitmap(width, height);

            int count = 0;
            foreach (KeyValuePair<int, int> clusterSizeKvp in clusterSizeList)
            {
                int clusterId = clusterSizeKvp.Key;
                if (count > 100)
                    break;

                foreach (Position position in objectPatches)
                {
                    if (position.HACCluster != clusterId)
                        continue;

                    //bmp.SetPixel(pix.Position.X - minX, pix.Position.Y - minY, pix.color);//shift position by minX and minY                   
                    int left = position.X - patchSize;
                    int right = position.X + patchSize;
                    int top = position.Y + patchSize;
                    int bottom = position.Y - patchSize;

                    Color patchColour = colorDict[position.HACCluster];

                    for (int x = left; x < right; x++)
                    {
                        for (int y = bottom; y < top; y++)
                            bmp.SetPixel(x - minX, y - minY, patchColour);//shift position by minX and minY
                    }

                }
                count++;
            }
                
          
            return bmp;
        }

        private static IEnumerable<KeyValuePair<int, int>> GetClusterSizeList(List<Position> positions)
        {
            List<int> clusterSizeList = new List<int>();
            
            Dictionary<int, int> sizeDict = new Dictionary<int, int>();

            foreach (Position pos in positions)
            {
                if (!sizeDict.ContainsKey(pos.HACCluster))
                    sizeDict.Add(pos.HACCluster, 0);

                sizeDict[pos.HACCluster] += 1;
            }

            // sort by value desc
            var sortedDict = from entry in sizeDict orderby entry.Value descending select entry;
            
            return sortedDict;
        }

        private static Bitmap CreateObjectSliceBitmap(List<Position> objectPatches, Dictionary<int, Color> colorDict, int clusterId, int patchSize)
        {

            int minX = objectPatches.Min(p => p.X) - patchSize;
            int maxX = objectPatches.Max(p => p.X) + patchSize;

            int minY = objectPatches.Min(p => p.Y) - patchSize;
            int maxY = objectPatches.Max(p => p.Y) + patchSize;

            int width = maxX + 1 - minX;
            int height = maxY + 1 - minY;

            var bmp = new Bitmap(width, height);

            foreach (Position position in objectPatches)
            {
                if (position.HACCluster != clusterId) 
                    continue;

                //bmp.SetPixel(pix.Position.X - minX, pix.Position.Y - minY, pix.color);//shift position by minX and minY
                int left = position.X - patchSize;
                int right = position.X + patchSize;
                int top = position.Y + patchSize;
                int bottom = position.Y - patchSize;

                Color patchColour = colorDict[position.HACCluster];

                for (int x = left; x < right; x++)
                {
                    for (int y = bottom; y < top; y++)
                        bmp.SetPixel(x - minX, y - minY, patchColour);//shift position by minX and minY
                }

            }

            return bmp;
        }

    }
}
/*
    private static Bitmap CreateBitmap(List<Position> objectPatches, int width, int height, int patchSize)
    {
        var bmp = new Bitmap(width, height);

        foreach (Position position in objectPatches)
        {
            Random randomGen = new Random();
            KnownColor[] names = (KnownColor[])Enum.GetValues(typeof(KnownColor));
            KnownColor randomColorName = names[randomGen.Next(names.Length)];
            Color randomColor = Color.FromKnownColor(randomColorName);
            int left = position.X - patchSize;
            int right = position.X + patchSize;
            int top = position.Y + patchSize;
            int bottom = position.Y - patchSize;

            for (int x = left; x < right; x++)
            {
                for (int y = bottom; y < top; y++)
                    bmp.SetPixel(x, y, randomColor);//shift position by minX and minY
            }                
        }

        return bmp;
    }
         
  public static void Process(List<int[]> positions, List<int[]> dci, List<int[]> dHacCI)
  {
      List<Position> posObjs = ConvertPositions(positions);

      // CREATE Image Segmentation

      Position[,] posArray = new Position[12300, 8300];
      int windowSize = 8;
      // add to posArray
      for (int i = 0; i < positions.Count; i++)
      {
          Position pos = posObjs[i];
          posArray[pos.Y, pos.X] = pos;
      }

      // sort by X
      //posObjs.Sort(Position.SortByX);

      int arraySize = windowSize * 2;
      short[] patch = new short[arraySize];

      List<List<Position>> disconnectedComponents = new List<List<Position>>();

      Dictionary<Position, bool> processedPositions = new Dictionary<Position, bool>();

      int objectCount = 0;
      for (int i = 0; i < posObjs.Count; i++)
      {
          Position p = posObjs[i];
          if (processedPositions.ContainsKey(p))
              continue; // already processed so continue

          ProcessPosition(p, posArray, processedPositions);

                
      }
  }

  public static void ProcessPosition(
      Position p, 
      Position[,] posArray, 
      Dictionary<Position, bool> processedPositions,
      Graph graph)
  {
      Position[] overlaps = FindOverlapping(p, posArray);
      foreach (Position overlap in overlaps)
      {
          ProcessPosition(overlap, posArray, processedPositions);
      }

      Position[] overlapping = FindOverlapping(p, posArray);




      processedPositions.Add(p, true);
      for (int j = 0; j < overlaps.Length; j++)
          processedPositions.Add(overlaps[j], true);
  }

  public static Position[] FindOverlapping(Position p, Position[,] posArray)
  {

      return null;
  }

 * 
 * List<int[]> reduced = GetReducedHACClusterList(cp.HACProximityCounts, clusterSizeList, maxClusterId);
            int[,] proxCounts = cp.HACProximityCounts;
            //CsvParserHelper.SaveTxt(outputPath + "/hac_proximity_counts_winsize2.txt", proxCounts, ndim: maxClusterId, colDelimiter: ',');
            CsvParserHelper.SaveTxt(outputPath + "reduced_hac_proximity_counts_winsize2.txt", reduced, colDelimiter: ',');

  */

/*
public static Dictionary<int, List<ObjectCentre>> DeblendObjects(
    Dictionary<int, List<Position>> objects, Dictionary<int, int> clusterStrength, int windowSize, int maxDistance, int minBlobDistance=25)
{
    Dictionary<int, List<ObjectCentre>> finalCentres = new Dictionary<int, List<ObjectCentre>>();

    PositionComparerX cpX = new PositionComparerX();
            
    foreach(int blobKey in objects.Keys)
    {
        List<Position> blob = objects[blobKey];

        // convert list of positions to dictionary keyed by HACClusterId
        Dictionary<int, List<Position>> labelPatches = new Dictionary<int, List<Position>>();
        foreach (Position p in blob)
        {
            if (!labelPatches.ContainsKey(p.HACCluster))
                labelPatches.Add(p.HACCluster, new List<Position>());

            var positions = labelPatches[p.HACCluster];
            positions.Add(p);
        }


        List<ObjectCentre> potentialBlobCentres = new List<ObjectCentre>();

        // for each HACCLusterId identify possible sub objects and their centres
        // loop through by strength? or weakness??
        foreach(int HACClusterId in labelPatches.Keys)
        {
            List<Position> labelPositions = labelPatches[HACClusterId];

            // need to call for each cluster id
            labelPositions.Sort(cpX);
            ClosestPatches cp = new ClosestPatches(labelPositions, cpX, windowSize, maxDistance);
            SubObjectConnComps socc = new SubObjectConnComps(cp);
            Dictionary<int, List<Position>> subObjects = socc.Find(labelPositions, null, windowSize);

            //int strength = clusterStrength[HACClusterId];
            int strength = 0;

            // loop through potential sub objects
            foreach (List<Position> subBlob in subObjects.Values)
            {
                Point muCentre = GetObjectCentre(subBlob);
                Rectangle rect = FindObjectDimensions(subBlob, windowSize);
                potentialBlobCentres.Add(new ObjectCentre(muCentre.X, muCentre.Y, rect, strength, HACClusterId, false));   
            }
        }

        // got list of blob centres for each clusterid now find which ones match. 
        List<ObjectCentre> blobCentres = GetBlobCentresFromPotentials(potentialBlobCentres, minBlobDistance);
        if (finalCentres.ContainsKey(blobKey))
            Console.WriteLine("ERror key shouldnt be there");
        finalCentres.Add(blobKey, blobCentres);
    }

    return finalCentres;
}
 * */
/*
private static List<ObjectCentre> GetBlobCentresFromPotentials(List<ObjectCentre> potentialBlobCentres, int minBlobDistance)
{
    Dictionary<int, ObjectCentre> finalCentres = new Dictionary<int, ObjectCentre>();
    int blobCount = 0;

    // loop through blob clusters and identify which ones are close to each other.
    foreach (ObjectCentre potentialCentre in potentialBlobCentres)
    {                
        if (finalCentres.Count == 0)
        {
            finalCentres.Add(blobCount, potentialCentre);
            blobCount++;
            continue;
        }

        bool foundCentre = false;
        foreach (int finalCentreId in finalCentres.Keys)
        {
            ObjectCentre finalOC = finalCentres[finalCentreId];

            if (finalOC.Distance(potentialCentre) < minBlobDistance)
            {
                finalOC.BlobCentres.Add(potentialCentre);
                foundCentre = true;
                break;
            }
        }
        if (!foundCentre)
        {
            finalCentres.Add(blobCount, potentialCentre);
            blobCount++;
        }
    }

    foreach (int blobId in finalCentres.Keys)
    {
        ObjectCentre finalCentre = finalCentres[blobId];

        int left = 0;
        int top = 0;
        int right = 0;
        int bottom = 0;
        foreach (ObjectCentre cluster in finalCentre.BlobCentres)
        {
            cluster.Rect.Left

        }
    }

    // loop through finalcentres and identify which ones encompass inner centres. if the outer one contains points that are greater than min blob distance,
    // then outer is probably background so ditch.

    return finalCentres.Values.ToList<ObjectCentre>();
}
*/