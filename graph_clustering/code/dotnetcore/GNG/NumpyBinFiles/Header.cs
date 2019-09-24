using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;
using System.Text.RegularExpressions;

namespace NumpyBinFiles
{
    public class Header
    {
        public char[] MagicString;
        public String HeaderString;
        public byte MajorVersion;
        public byte MinorVersion;
        public long HeaderLength;
        public long DataLength;
        public long HeaderStartPos;
        public long DataStartPos;
        public long NumRows;
        public long NumCols;
        public long FileSize;       // in bytes
        public long StreamLength;   // in bytes
        public byte TypeSize = 4;   // in bytes


        public static Header ParseHeader(String filePath, long position)
        {
            Header h = new Header();

            h.FileSize = new FileInfo(filePath).Length;

            using (FileStream fs = File.OpenRead(filePath))
            {
                h.StreamLength = fs.Length;

                if (position > 0)
                    fs.Seek(position, SeekOrigin.Begin);

                h.HeaderStartPos = position;

                BinaryReader br = new BinaryReader(fs);

                // read magic string 6 bytes
                h.MagicString = br.ReadChars(6);
                h.MajorVersion = br.ReadByte();
                h.MinorVersion = br.ReadByte();
                //int headerLen = -1;
                if (h.MajorVersion == 2)
                {
                    int numHeaderBytes = 4;
                    byte[] headerLenBytes = br.ReadBytes(numHeaderBytes); // little-endian
                    h.HeaderLength = (int)BitConverter.ToUInt32(headerLenBytes, 0);
                    h.DataStartPos = (uint)(8 + numHeaderBytes + (h.HeaderLength) + h.HeaderStartPos);
                }

                if (h.MajorVersion == 1)
                {
                    int numHeaderBytes = 2;
                    byte[] headerLenBytes = br.ReadBytes(numHeaderBytes); // little-endian
                    h.HeaderLength = BitConverter.ToUInt16(headerLenBytes, 0);
                    h.DataStartPos = (uint)(8 + numHeaderBytes + (h.HeaderLength) + h.HeaderStartPos);
                }

                // read header
                byte[] headerBytes = br.ReadBytes((int)h.HeaderLength);

                h.HeaderString = System.Text.Encoding.ASCII.GetString(headerBytes);

                // {'descr': '<f4', 'fortran_order': False, 'shape': (26L, 43L), }      \n

                //String pattern = @"{'descr': '([<>a-z0-9]+)', 'fortran_order': ([True|False]), 'shape': \(([0-9]+)L, ([0-9]+)L\), }";
                String pattern = @"{'descr': '([<>a-z0-9]+)', 'fortran_order': (True|False), 'shape': \(([0-9]+)[L]?, ([0-9]+)[L]?\), }";
                Regex rgx = new Regex(pattern);
                Match m = rgx.Match(h.HeaderString);
                if (m.Success)
                {
                    //Console.WriteLine("Successfully matched header string");
                    String dtype = m.Groups[1].Value;

                    bool fortranOrder = (m.Groups[2].Value == "True") ? true : false;
                    h.NumRows = UInt32.Parse(m.Groups[3].Value);
                    h.NumCols = UInt32.Parse(m.Groups[4].Value);
                }
                else
                    Console.WriteLine("Error: Failed to match header string: {0}", h.HeaderString);
            }

            return h;            
        }

        public override String ToString()
        {
            return this.HeaderString + 
                String.Format(" hdr size: {0}  data size: {1}  data offset: {2} num rows: {3} num cols: {4}", 
                this.HeaderLength, this.DataLength, this.DataStartPos, this.NumRows, this.NumCols);
        }
    }
}
