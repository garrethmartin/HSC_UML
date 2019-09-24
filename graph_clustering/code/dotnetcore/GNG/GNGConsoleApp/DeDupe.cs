using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GNGConsoleApp
{
    class DeDupe
    {
        public static List<int> Dedupe(HashSet<String> antiDupeList, List<float[]> samples, int decimalPlaces)
        {

            var okList = new List<int>();
            /*
            int recLength = samples[0].Length;
            double[] t = new double[recLength];
            for (int i=0;i<samples.Count;i++)
            {
                
                for (int j = 0; j < recLength; j++)
                {
                    t[j] = Math.Round(samples[i][j], decimalPlaces);
                }

                String strRep = String.Join("", t);
                if (antiDupeList.Add(strRep))
                    okList.Add(i);
            }
            */
            Console.WriteLine("Samples count: {0} Unique count: {1}", samples.Count, okList.Count);
            return okList;
            /*
            // round the values and try add to hash, if not, then skip. Is linear (but have to change to string).
            // Math.Round(f, 5);
            // use a set
            HashSet<String> hs = new HashSet<String>();

            float[] a = { 1.23f, 12.001f, 34.211f };
            float[] b = { 1.23f, 12.001f, 34.211f };

            String astr = String.Join("", a);
            String bstr = String.Join("", b);

            hs.Add(astr);
            hs.Add(bstr);

            Console.WriteLine(hs.Count);

            return dupeList;
            */
        }
    }
}
