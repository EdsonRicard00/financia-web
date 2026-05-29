const express = require('express');
const cors = require('cors');
const multer = require('multer');
const xml2js = require('xml2js');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

const app = express();
const port = 5000;

// Configuração de UX/Segurança: Permite que o Frontend aceda ao Backend
app.use(cors());
app.use(express.json());

// Configuração do Multer para receber múltiplos ficheiros na memória (sem encher o disco do servidor)
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// ROTA PRINCIPAL: Onde a magia da conversão e unificação acontece
app.post('/api/merge', upload.array('files'), async (req, res) => {
    try {
        const files = req.files;
        if (!files || files.length === 0) {
            return res.status(400).json({ error: 'Nenhum ficheiro foi enviado.' });
        }

        // Criamos um documento PDF principal em branco usando a pdf-lib
        const pdfUnificado = await PDFDocument.create();
        const parser = new xml2js.Parser({ explicitArray: false });

        // Percorremos todos os ficheiros enviados pelo colaborador
        for (const file of files) {
            if (file.mimetype === 'application/pdf' || file.originalname.endsWith('.pdf')) {
                // Se for PDF, carregamos o documento
                const pdfDoc = await PDFDocument.load(file.buffer);
                // Copiamos todas as páginas dele para o nosso PDF unificado
                const paginasCopiadas = await pdfUnificado.copyPages(pdfDoc, pdfDoc.getPageIndices());
paginasCopiadas.forEach((pagina) => pdfUnificado.addPage(pagina));
                paginasCopiadas.forEach((pagina) => pdfUnificado.addPage(pagina));
            } 
            else if (file.mimetype === 'text/xml' || file.originalname.endsWith('.xml')) {
                // SE FOR XML DA NF-e:
                const xmlContent = file.buffer.toString('utf-8');
                
                // Fazemos o parse do XML para ler os dados da Nota Fiscal
                const resultadoJson = await parser.parseStringPromise(xmlContent);
                
                // Apenas para testes no terminal: Extrai a Chave de Acesso da NF-e (Padrão SEFAZ)
                const chNFe = resultadoJson?.nfeProc?.protNFe?.infProt?.chNFe || 'Não encontrada';
                console.log(`📌 NF-e Processada com sucesso! Chave: ${chNFe}`);

                // NOTA DE DESIGN/UX: Aqui vamos injetar a lógica de transformar os dados do XML num layout DANFE bonito.
                // Por agora, para avançarmos na estrutura, o motor foca em unificar os PDFs existentes.
            }
        }

        // Guarda o PDF final unificado em Bytes
        const pdfBytes = await pdfUnificado.save();

        // Envia o PDF final de volta para a interface do utilizador
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename=nfe_unificada.pdf');
        res.send(Buffer.from(pdfBytes));

    } catch (error) {
        console.error('Erro no processamento:', error);
        res.status(500).json({ error: 'Erro interno ao processar os ficheiros.' });
    }
});

// Inicia o servidor na porta 5000
app.listen(port, () => {
    console.log(`🚀 Motor SmartMerge a rodar em http://localhost:${port}`);
});