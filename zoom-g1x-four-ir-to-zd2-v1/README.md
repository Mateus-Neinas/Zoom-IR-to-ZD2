# Zoom G1X FOUR — IR to ZD2

Ferramenta experimental para converter um arquivo WAV PCM em um efeito `.ZD2` baseado no modelo `IRCAB_IR_ICON.ZD2`, destinado ao fluxo de importação do Zoom Effect Manager.

## Estado do projeto

- **Uma IR por vez:** o conversor gera um arquivo `.ZD2` por operação.
- **Nome no visor:** na Zoom G1X FOUR, o efeito aparece como **IR CAB**. O nome do arquivo de saída não altera o nome apresentado no visor.
- **Importação:** use o Zoom Effect Manager para transferir o arquivo gerado.
- **Compatibilidade:** projeto experimental. Faça backup dos efeitos e teste com cuidado; a conversão não é uma ferramenta oficial da Zoom.

## Formatos de entrada

O conversor aceita WAV PCM sem compressão, mono ou estéreo. O áudio estéreo é reduzido a mono. O algoritmo escreve 696 taps float32 no bloco `ir_taps` do modelo.

## Uso

1. Abra o programa.
2. Selecione o WAV de entrada.
3. Escolha o caminho e o nome do arquivo `.ZD2`.
4. Informe um nome de efeito de até 11 caracteres (o visor da pedaleira continuará mostrando `IR CAB`).
5. Clique em **Converter para ZD2**.
6. Importe o arquivo gerado com o Zoom Effect Manager.

## Compilar

É necessário instalar Python 3 e ter o Tk/Tkinter disponível na instalação.

### Windows

```bat
build_windows.bat
```

O executável será criado em `dist/Zoom_G1X_FOUR_IR_to_ZD2.exe`.

### macOS

```bash
chmod +x build_macos.sh
./build_macos.sh
```

O executável será criado em `dist/Zoom_G1X_FOUR_IR_to_ZD2`.

### Linux

```bash
chmod +x build_linux.sh
./build_linux.sh
```

O executável será criado em `dist/Zoom_G1X_FOUR_IR_to_ZD2`.

**Importante:** compile em cada sistema operacional de destino; o PyInstaller não produz, em geral, um único binário universal para Windows, macOS e Linux. No Linux, pode ser necessário instalar o pacote de Tkinter da distribuição (por exemplo, `python3-tk`).

## Limitações conhecidas

- Gera somente uma IR por vez.
- O efeito será exibido como `IR CAB` na pedaleira.
- O formato e o tratamento da IR são experimentais; não há garantia de compatibilidade acústica para todo WAV.
- O arquivo-modelo `IRCAB_IR_ICON.ZD2` é incluído para fins de funcionamento deste projeto; confirme os direitos e termos aplicáveis antes de redistribuir publicamente.

## Aviso

Projeto comunitário, sem vínculo com a Zoom Corporation. Use por sua conta e risco e mantenha cópias de segurança.
