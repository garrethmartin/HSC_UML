using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AgglomerativeClustering
{
    public class PearsonAndDC : Similarity
    {
        private int numPowerSpectrums = -1;
        private int numValsInPowerSpectrum = -1;
        private Similarity ps = new PeasonSimilarity();

        public PearsonAndDC(int numPowerSpectrums)
        {
            this.numPowerSpectrums = numPowerSpectrums;
        }
        public PearsonAndDC(int numPowerSpectrums, int numValsInPowerSpectrum)
        {
            this.numValsInPowerSpectrum = numValsInPowerSpectrum;
            this.numPowerSpectrums = numPowerSpectrums;
        }

        double Similarity.GetDistance(BiCluster one, BiCluster two)
        {
            double distance = ps.GetDistance(one, two);

            if (numValsInPowerSpectrum == -1)
                numValsInPowerSpectrum = one.Vector.Length / numPowerSpectrums;

            int zeroDCIndex = 0;
            for (int i = 0; i < numPowerSpectrums; i++)
            {
                double diff = Math.Abs(one.Vector[zeroDCIndex] - two.Vector[zeroDCIndex]);
                if (diff > 0.2)
                    distance += 0.2;

                zeroDCIndex += numValsInPowerSpectrum;
            }


            return distance;
        }
    }
}
