import { useRef, useState, type DragEvent, type ReactNode } from "react";

interface FileDropzoneProps {
  file: File | null;
  onChange: (file: File | null) => void;
  accept?: string;
  maxBytes?: number;
}

const DEFAULT_ACCEPT = "image/jpeg,image/png,image/webp,application/pdf";
const DEFAULT_MAX = 10 * 1024 * 1024;

export function FileDropzone({
  file,
  onChange,
  accept = DEFAULT_ACCEPT,
  maxBytes = DEFAULT_MAX,
}: FileDropzoneProps): ReactNode {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isOver, setIsOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function validateAndSet(picked: File | null): void {
    setError(null);
    if (!picked) {
      onChange(null);
      return;
    }
    if (!accept.split(",").includes(picked.type)) {
      setError(`Tipo no soportado: ${picked.type}`);
      onChange(null);
      return;
    }
    if (picked.size > maxBytes) {
      setError(`El archivo supera ${(maxBytes / (1024 * 1024)).toFixed(0)} MB`);
      onChange(null);
      return;
    }
    onChange(picked);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>): void {
    event.preventDefault();
    setIsOver(false);
    const picked = event.dataTransfer.files[0] ?? null;
    validateAndSet(picked);
  }

  return (
    <div className="space-y-2">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsOver(true);
        }}
        onDragLeave={() => setIsOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors ${
          isOver
            ? "border-brand-500 bg-brand-50"
            : "border-slate-300 bg-white hover:border-brand-400"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => validateAndSet(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-slate-900">{file.name}</p>
            <p className="text-xs text-slate-500">
              {(file.size / 1024).toFixed(1)} KB - {file.type}
            </p>
            <button
              type="button"
              className="mt-2 text-xs text-brand-700 underline"
              onClick={(e) => {
                e.stopPropagation();
                validateAndSet(null);
              }}
            >
              Reemplazar archivo
            </button>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-700">
              Arrastra un archivo o hace click para seleccionarlo
            </p>
            <p className="text-xs text-slate-500">PDF, JPG, PNG, WEBP. Maximo 10 MB.</p>
          </div>
        )}
      </div>
      {error && <p className="text-xs text-rose-700">{error}</p>}
    </div>
  );
}
