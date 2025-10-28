"""
Edge TTS Worker para IADvogado
Implementação básica do Text-to-Speech usando Microsoft Edge TTS
"""

import edge_tts
import asyncio
import logging
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from ..config.config import settings

logger = logging.getLogger(__name__)

class EdgeTTSWorker:
    """Worker para conversão de texto em áudio usando Edge TTS"""
    
    def __init__(self):
        self.voice = settings.tts_voice
        self.rate = settings.tts_rate
        self.volume = settings.tts_volume
        self.pitch = settings.tts_pitch
        self.use_ssml = settings.tts_use_ssml
        self.cache_enabled = settings.tts_cache_enabled
        self.cache_ttl = settings.tts_cache_ttl
        
        # Configurar diretório de cache
        self.cache_dir = "audio_cache"
        if self.cache_enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Cache de áudio habilitado: {self.cache_dir}")
        
        # Métricas de performance
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_generation_time": 0.0,
            "total_cache_size": 0
        }
        
        logger.info(f"EdgeTTSWorker inicializado - Voz: {self.voice}, SSML: {self.use_ssml}, Cache: {self.cache_enabled}")
    
    def _get_cache_key(self, text: str, voice: str, rate: str, volume: str, pitch: str) -> str:
        """Gera chave única para cache baseada nos parâmetros"""
        content = f"{text}|{voice}|{rate}|{volume}|{pitch}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Retorna caminho completo do arquivo de cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.mp3")
    
    def _is_cache_valid(self, cache_file: str) -> bool:
        """Verifica se o arquivo de cache ainda é válido"""
        if not os.path.exists(cache_file):
            return False
        
        file_time = os.path.getmtime(cache_file)
        expiry_time = (datetime.now() - timedelta(seconds=self.cache_ttl)).timestamp()
        return file_time > expiry_time
    
    def _get_cache_size(self) -> int:
        """Calcula tamanho total do cache em bytes"""
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return 0
        
        total_size = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.mp3'):
                filepath = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(filepath)
        
        return total_size
    
    def _clean_expired_cache(self):
        """Remove arquivos de cache expirados"""
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return
        
        expired_files = []
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.mp3'):
                filepath = os.path.join(self.cache_dir, filename)
                if not self._is_cache_valid(filepath):
                    expired_files.append(filepath)
        
        for filepath in expired_files:
            try:
                os.remove(filepath)
                logger.debug(f"Arquivo de cache expirado removido: {filepath}")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo de cache: {e}")
    
    async def get_available_voices(self, language: str = "pt-BR") -> List[Dict]:
        """
        Lista todas as vozes disponíveis para um idioma
        
        Args:
            language: Código do idioma (ex: pt-BR, pt-PT)
        
        Returns:
            Lista de dicionários com informações das vozes
        """
        try:
            voices = await edge_tts.list_voices()
            filtered_voices = [v for v in voices if v['Locale'].startswith(language)]
            
            logger.info(f"Encontradas {len(filtered_voices)} vozes para {language}")
            return filtered_voices
            
        except Exception as e:
            logger.error(f"Erro ao listar vozes: {e}")
            return []
    
    async def text_to_speech_bytes(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None
    ) -> bytes:
        """
        Converte texto em áudio usando Edge TTS com cache
        
        Args:
            text: Texto para converter
            voice: Voz específica (opcional)
            rate: Velocidade da fala (opcional)
            volume: Volume do áudio (opcional)
            pitch: Tom da voz (opcional)
        
        Returns:
            bytes: Áudio em formato MP3
        """
        import time
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Usar parâmetros fornecidos ou padrões
            voice = voice or self.voice
            rate = rate or self.rate
            volume = volume or self.volume
            pitch = pitch or self.pitch
            
            # Verificar cache primeiro
            if self.cache_enabled:
                cache_key = self._get_cache_key(text, voice, rate, volume, pitch)
                cache_file = self._get_cache_file_path(cache_key)
                
                if self._is_cache_valid(cache_file):
                    logger.info(f"Cache hit para texto de {len(text)} caracteres")
                    self.metrics["cache_hits"] += 1
                    
                    with open(cache_file, 'rb') as f:
                        audio_data = f.read()
                    
                    # Atualizar métricas
                    generation_time = time.time() - start_time
                    self.metrics["avg_generation_time"] = (
                        (self.metrics["avg_generation_time"] * (self.metrics["total_requests"] - 1) + generation_time) 
                        / self.metrics["total_requests"]
                    )
                    
                    logger.info(f"Áudio carregado do cache: {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.info(f"Cache miss para texto de {len(text)} caracteres")
                    self.metrics["cache_misses"] += 1
            
            logger.info(f"Gerando áudio - Voz: {voice}, Rate: {rate}, Volume: {volume}, Pitch: {pitch}")
            
            # Gerar áudio
            if self.use_ssml:
                ssml = self.create_ssml_for_legal_text(text, voice)
                audio_data = await self._generate_audio_from_ssml(ssml, voice)
            else:
                audio_data = await self._generate_audio_from_text(text, voice, rate, volume, pitch)
            
            # Salvar no cache se habilitado
            if self.cache_enabled:
                try:
                    with open(cache_file, 'wb') as f:
                        f.write(audio_data)
                    logger.debug(f"Áudio salvo no cache: {cache_file}")
                    
                    # Limpar cache expirado periodicamente
                    if self.metrics["total_requests"] % 10 == 0:
                        self._clean_expired_cache()
                        
                except Exception as e:
                    logger.warning(f"Erro ao salvar no cache: {e}")
            
            # Atualizar métricas
            generation_time = time.time() - start_time
            self.metrics["avg_generation_time"] = (
                (self.metrics["avg_generation_time"] * (self.metrics["total_requests"] - 1) + generation_time) 
                / self.metrics["total_requests"]
            )
            self.metrics["total_cache_size"] = self._get_cache_size()
            
            logger.info(f"Áudio gerado com sucesso: {len(audio_data)} bytes em {generation_time:.2f}s")
            return audio_data
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            raise
    
    async def _generate_audio_from_text(self, text: str, voice: str, rate: str, volume: str, pitch: str) -> bytes:
        """Gera áudio a partir de texto simples"""
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    async def _generate_audio_from_ssml(self, ssml: str, voice: str) -> bytes:
        """Gera áudio a partir de SSML"""
        communicate = edge_tts.Communicate(ssml, voice)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    def create_ssml_for_legal_text(self, text: str, voice: str = None) -> str:
        """
        Cria SSML otimizado para texto jurídico
        
        Args:
            text: Texto jurídico para converter
            voice: Voz específica (opcional)
        
        Returns:
            str: SSML formatado
        """
        voice = voice or self.voice
        
        # Limpar texto para SSML (escapar caracteres especiais)
        clean_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Criar SSML otimizado para texto jurídico
        ssml = f"""<speak version="1.0"
       xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts"
       xml:lang="pt-BR">
  <voice name="{voice}">
    <mstts:express-as style="narration-professional">
      <prosody rate="{self.rate}" pitch="{self.pitch}" volume="{self.volume}">
        {clean_text}
      </prosody>
    </mstts:express-as>
  </voice>
</speak>""".strip()
        
        logger.debug(f"SSML gerado para texto de {len(text)} caracteres")
        return ssml
    
    async def test_voice(self, voice: str, test_text: str = "Olá, este é um teste de voz.") -> bool:
        """
        Testa se uma voz está funcionando corretamente
        
        Args:
            voice: Nome da voz para testar
            test_text: Texto de teste
        
        Returns:
            bool: True se a voz funcionar, False caso contrário
        """
        try:
            audio_data = await self._generate_audio_from_text(test_text, voice, "+0%", "+0%", "+0Hz")
            return len(audio_data) > 0
        except Exception as e:
            logger.error(f"Erro ao testar voz {voice}: {e}")
            return False
    
    def get_metrics(self) -> Dict:
        """Retorna métricas de performance do TTS"""
        self.metrics["total_cache_size"] = self._get_cache_size()
        return self.metrics.copy()
    
    def clear_cache(self) -> int:
        """Limpa todo o cache e retorna número de arquivos removidos"""
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return 0
        
        removed_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.mp3'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao remover arquivo de cache: {e}")
        
        logger.info(f"Cache limpo: {removed_count} arquivos removidos")
        return removed_count
    
    def get_cache_info(self) -> Dict:
        """Retorna informações sobre o cache"""
        if not self.cache_enabled:
            return {"enabled": False}
        
        cache_size = self._get_cache_size()
        file_count = 0
        
        if os.path.exists(self.cache_dir):
            file_count = len([f for f in os.listdir(self.cache_dir) if f.endswith('.mp3')])
        
        return {
            "enabled": True,
            "cache_dir": self.cache_dir,
            "file_count": file_count,
            "total_size_bytes": cache_size,
            "total_size_mb": round(cache_size / (1024 * 1024), 2),
            "ttl_seconds": self.cache_ttl,
            "cache_hit_rate": round(
                (self.metrics["cache_hits"] / max(1, self.metrics["total_requests"])) * 100, 2
            )
        }

# Instância global do worker
edge_tts_worker = EdgeTTSWorker()

# Função de compatibilidade com código existente
async def text_to_speech_bytes(text: str) -> bytes:
    """
    Função de compatibilidade para o código existente
    Substitui a função do gTTS
    """
    return await edge_tts_worker.text_to_speech_bytes(text)

# Função para listar vozes disponíveis
async def list_available_voices(language: str = "pt-BR") -> List[Dict]:
    """Lista vozes disponíveis para um idioma"""
    return await edge_tts_worker.get_available_voices(language)
