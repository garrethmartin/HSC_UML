using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Globalization;

namespace CSVParser
{
    public class CsvParserHelper
    {

        public static List<float[]> LoadFloats(String filePath)
        {
            Console.WriteLine("Loading ... {0}", filePath);

            List<float[]> data = new List<float[]>();
            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser parser = new CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                float[] sample = new float[ndim];
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] = float.Parse(ssample[i], NumberStyles.Float);
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} records.", data.Count);
            return data;
        }

        public static List<double[]> LoadDoubles(String filePath)
        {
            Console.WriteLine("Loading ... {0}", filePath);

            var data = new List<double[]>();

            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser parser = new CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                double[] sample = new double[ndim];
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] = double.Parse(ssample[i], NumberStyles.Float);
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} records.", data.Count);
            return data;
        }

        public static List<int[]> LoadInts(String filePath)
        {
            Console.WriteLine("Loading ... {0}", filePath);

            List<int[]> data = new List<int[]>();
            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser parser = new CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                int[] sample = new int[ndim];
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] = int.Parse(ssample[i], NumberStyles.Float);
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} records,", data.Count);
            return data;
        }

        public static List<int[]> LoadDecimals(String filePath)
        {
            Console.WriteLine("Loading ... {0}", filePath);

            List<int[]> data = new List<int[]>();
            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser parser = new CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                int[] sample = new int[ndim];
                for (int i = 0; i < ndim; i++)
                {
                    //decimal d = Decimal.Parse("1.2345E-02", System.Globalization.NumberStyles.Float);
                    decimal d = Decimal.Parse(ssample[i], System.Globalization.NumberStyles.Float);
                    sample[i] = Convert.ToInt32(d); //int.Parse(ssample[i]);
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} records.", data.Count);
            return data;
        }

        public static void SaveTxt(String filePath, List<String> data, String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                foreach (String line in data)
                {
                    sw.Write(line);
                    sw.Write(lineDelimiter);
                }

            }
        }

        public static void SaveTxt(String filePath, List<int[]> data, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                foreach (int[] line in data)
                {
                    for (int i = 0; i < line.Length; i++)
                    {
                        int col = line[i];
                        sw.Write(col.ToString());
                        if (i < line.Length - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }

        public static void SaveTxt(String filePath, int[] data, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            var newData = new List<int[]>();
            newData.Add(data);
            SaveTxt(filePath, newData, colDelimiter, lineDelimiter);
        }


        public static void SaveTxt(String filePath, List<float[]> data, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                for (int i = 0; i < data.Count; i++)
                {
                    float[] line = data[i];
                    for (int j = 0; j < line.Length; j++)
                    {
                        sw.Write(line[j].ToString());
                        if (j < line.Length - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }

        public static void SaveTxt(String filePath, List<double[]> data, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            /*
            using (StreamWriter sw = new StreamWriter(filePath, false))
            {
                foreach (double[] line in data)
                {
                    for (int i = 0; i < line.Length; i++)
                    {
                        double col = line[i];

                        sw.Write(col.ToString());
                        if (i < line.Length - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
            */
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                for (int i = 0; i < data.Count; i++)
                {
                    double[] line = data[i];
                    for (int j = 0; j < line.Length; j++)
                    {
                        sw.Write(line[j].ToString());
                        if (j < line.Length - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }

        }

        public static void SaveTxt(String filePath, int[,] data, int ndim, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            int numSamples = data.Length / ndim;

            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath, false))
            {
                for (int i = 0; i < numSamples; i++)
                {
                    for (int j = 0; j < ndim; j++)
                    {
                        sw.Write(data[i, j]);
                        if (j != ndim - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }

        public static Dictionary<int, int> LoadIntsDict(String filePath)
        {
            Console.WriteLine("Loading ... {0}", filePath);

            var data = new Dictionary<int, int>();

            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser parser = new CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                int key = int.Parse(ssample[0], NumberStyles.Float);
                int value = int.Parse(ssample[1], NumberStyles.Float);
                data.Add(key, value);
            }

            Console.WriteLine("Loaded {0} records,", data.Count);
            return data;
        }

        public static void SaveTxt(String filePath, Dictionary<int, int> data, char colDelimiter = ',', String lineDelimiter = "\r\n")
        {
            Dictionary<int, int>.KeyCollection keys = data.Keys;

            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath, false))
            {
                foreach (int key in keys)
                {
                    int value = data[key];
                    sw.Write(key);
                    sw.Write(colDelimiter);
                    sw.Write(value);
                    sw.Write(lineDelimiter);
                }
            }
        }
    
    }
}
