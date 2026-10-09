import type { ImportRow } from "./api";

export function parseContactsCsv(text: string): ImportRow[] {
  const rows: string[][] = [];
  let row: string[] = [],
    field = "",
    quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') {
        field += '"';
        i++;
      } else quoted = !quoted;
    } else if (c === ";" && !quoted) {
      row.push(field.trim());
      field = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field.trim());
      if (row.some((x) => x !== "")) rows.push(row);
      row = [];
      field = "";
    } else field += c;
  }
  if (quoted) throw new Error("O CSV contém aspas não fechadas.");
  row.push(field.trim());
  if (row.some((x) => x !== "")) rows.push(row);
  if (rows.shift()?.join(";").toLowerCase() !== "chave;nome;email;telefone")
    throw new Error("Use as colunas chave;nome;email;telefone, nesta ordem.");
  if (rows.length < 1 || rows.length > 100 || rows.some((r) => r.length !== 4))
    throw new Error("Use de 1 a 100 contatos, com quatro colunas por linha.");
  return rows.map((r) => ({
    externalKey: r[0],
    name: r[1],
    email: r[2],
    phone: r[3],
  }));
}
export function downloadContactsTemplate() {
  const blob = new Blob(
    [
      "\uFEFFchave;nome;email;telefone\r\nexemplo-001;Contato Exemplo;contato@cliente.example;5511999990002\r\n",
    ],
    { type: "text/csv;charset=utf-8" },
  );
  const url = URL.createObjectURL(blob),
    link = document.createElement("a");
  link.href = url;
  link.download = "modelo-contatos-ebt.csv";
  link.click();
  URL.revokeObjectURL(url);
}
