using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace CsvParser
{
    public class IOHelper
    {
        public static List<float[]> LoadFloats(String filePath)
        {
            Console.WriteLine("Loading floats...");

            List<float[]> data = new List<float[]>();
            string[][] s;
            using(TextReader tr = File.OpenText(filePath))
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
                    sample[i] = float.Parse(ssample[i]);                    
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} records", data.Count);
            return data;
        }

        public static List<int[]> LoadInts(String filePath)
        {
            var data = new List<int[]>();            
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
                    sample[i] = int.Parse(ssample[i]);
                }
                data.Add(sample);
            }

            return data;
        }


        public static void SaveTxt(String filePath, List<int[]> data, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                foreach (int[] line in data)
                {
                    foreach (int col in line)
                    {
                        sw.Write(col.ToString());
                        if (col != line[line.Length - 1])
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }


        public static void SaveTxt(String filePath, List<float[]> data, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                foreach (float[] line in data)
                {
                    foreach (float col in line)
                    {
                        sw.Write(col.ToString());
                        if (col != line[line.Length - 1])
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }

        public static void SaveTxt(String filePath, int[,] data, int ndim, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            int numSamples = data.Length / ndim;

            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
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
    }
}
