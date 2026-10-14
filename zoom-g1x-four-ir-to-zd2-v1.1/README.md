# Zoom G1X FOUR — IR to ZD2

Ferramenta experimental para converter um arquivo WAV PCM em um efeito `.ZD2` baseado no modelo `IRCAB_IR_ICON.ZD2`, destinado ao fluxo de importação do Zoom Effect Manager.

## Estado do projeto

A versão inclui uma correção experimental do campo de nome no visor. A compilação e a conversão devem ser testadas com um WAV de exemplo e na pedaleira antes de publicar como versão estável.

- **Uma IR por vez:** o conversor gera um arquivo `.ZD2` por operação.
- **Nome no visor:** a versão corrigida escreve o nome também no campo usado pelo visor da pedaleira. O nome exibido fica limitado a 6 caracteres; ainda precisa ser confirmado no hardware com diferentes nomes/modelos.
- **Importação:** use o Zoom Effect Manager para transferir o arquivo gerado.
- **Compatibilidade:** projeto experimental. Faça backup dos efeitos e teste com cuidado; a conversão não é uma ferramenta oficial da Zoom.

## Formatos de entrada

O conversor aceita WAV PCM sem compressão, mono ou estéreo. O áudio estéreo é reduzido a mono. O algoritmo escreve 696 taps float32 no bloco `ir_taps` do modelo.

## Uso

1. Abra o programa.
2. Selecione o WAV de entrada.
3. Escolha o caminho e o nome do arquivo `.ZD2`.
4. Informe um nome de efeito de até 6 caracteres para o visor.
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
- O nome no visor foi corrigido experimentalmente para até 6 caracteres; valide a exibição na sua pedaleira antes de considerar a versão estável.
- O formato e o tratamento da IR são experimentais; não há garantia de compatibilidade acústica para todo WAV.
- O arquivo-modelo `IRCAB_IR_ICON.ZD2` é incluído para fins de funcionamento deste projeto; confirme os direitos e termos aplicáveis antes de redistribuir publicamente.

## Aviso

Projeto comunitário, sem vínculo com a Zoom Corporation. Use por sua conta e risco e mantenha cópias de segurança.
