using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AgglomerativeClustering
{
    class PearsonGradientSimilarity : Similarity
    {
        private Similarity ps = new PeasonSimilarity();

        public PearsonGradientSimilarity()
        {
        }

        double Similarity.GetDistance(BiCluster one, BiCluster two)
        {
            double distance = ps.GetDistance(one, two);

            int length = one.Vector.Length - 1; // should be the same as length of two

            for (int i = 1; i < length; i++)
            {
                double gradOne = one.Vector[i] - one.Vector[i - 1];
                double gradTwo = two.Vector[i] - two.Vector[i - 1];

                if ((gradOne < 0 && gradTwo > 0) || (gradOne > 0 && gradTwo < 0))
                {
                    // grads are diffeerent
                    if (Math.Abs(gradOne - gradTwo) > 0.2)
                        distance += 0.2;
                }

            }

            return distance;
        }
    }
}
