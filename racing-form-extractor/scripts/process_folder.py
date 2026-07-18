import os
import sys
import glob
import subprocess

def process_folder(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    processed_dir = os.path.join(input_dir, "processed")
    failed_dir = os.path.join(input_dir, "failed")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)
    
    pdfs = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {input_dir}")
        return

    for pdf in pdfs:
        filename = os.path.basename(pdf)
        out_excel = os.path.join(output_dir, filename.replace(".pdf", ".xlsx"))
        
        # Simplified auto-detection for the stub:
        # We assume greyhound for this specific project context
        script_to_run = "greyhound_extract.py"
        
        print(f"Running {script_to_run} on {filename}...")
        
        try:
            result = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), script_to_run), pdf, out_excel], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Success: {filename}")
                if "INCOMPLETE" in result.stdout:
                    print(f"*** INCOMPLETE *** - {filename}")
                os.rename(pdf, os.path.join(processed_dir, filename))
            else:
                print(f"Failed: {filename}\n{result.stderr}")
                os.rename(pdf, os.path.join(failed_dir, filename))
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            os.rename(pdf, os.path.join(failed_dir, filename))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_folder.py input_dir output_dir")
        sys.exit(1)
    process_folder(sys.argv[1], sys.argv[2])
