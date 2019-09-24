using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SampleHandlerLib
{

    public class SkyArea
    {
        public int Id;
        public int Index;
        public String Field;
        public ulong NumSampleRows;
        public ulong NumSampleCols;
        public ulong NumMaxRows;
        public ulong NumMaxCols;
        public List<ImageFile> ImageFiles;
        
        public SkyArea(int id, int index)
        {
            this.Id = id;
            this.Index = index;
        }
        public SkyArea(int id, int index, String field) : this(id, index)
        {
            this.Field = field;

        }
    }

    public class RectangleS
    {
        public int Left;
        public int Right;
        public int Bottom;
        public int Top;

        public RectangleS(int bottom, int top, int left, int right)
        {
            Bottom = bottom;
            Top = top;
            Left = left;
            Right = right;
        }
    }

    public class ImageFile
    {
        public int Id;
        public String Wavelength;
        public String Filename;
        public String Sigma;
        public String threshold;
        public ImageFile(int id, String wavelength)
        {
            this.Id = id;
            this.Wavelength = wavelength;
        }
    }
}
