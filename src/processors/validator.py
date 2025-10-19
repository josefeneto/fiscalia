"""
Validador de dados de Notas Fiscais
Verifica consistência, formato e regras fiscais básicas
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Erro de validação de dados"""
    pass


class NFValidator:
    """Validador de Notas Fiscais"""
    
    # Padrões de validação
    CNPJ_PATTERN = re.compile(r'^\d{14}$')
    CPF_PATTERN = re.compile(r'^\d{11}$')
    CHAVE_NFE_PATTERN = re.compile(r'^\d{44}$')
    
    # Códigos válidos
    VALID_MODELOS = ['55', '65']  # 55=NFe, 65=NFCe
    VALID_TIPOS_OPERACAO = ['0', '1']  # 0=Entrada, 1=Saída
    
    def __init__(self):
        """Inicializa o validador"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, data: Dict[str, Any], strict: bool = False) -> bool:
        """
        Valida dados extraídos de uma Nota Fiscal
        
        Args:
            data: Dicionário com dados da NF
            strict: Se True, warnings também invalidam
            
        Returns:
            True se válido, False caso contrário
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Validações obrigatórias
            self._validate_metadata(data.get('metadados', {}))
            self._validate_emitente(data.get('emitente', {}))
            self._validate_destinatario(data.get('destinatario', {}))
            self._validate_valores(data.get('valores', {}))
            self._validate_itens(data.get('itens', []))
            
            # Validações de consistência
            self._validate_consistency(data)
            
        except ValidationError as e:
            self.errors.append(str(e))
        except Exception as e:
            logger.error(f"Erro inesperado na validação: {e}")
            self.errors.append(f"Erro inesperado: {str(e)}")
        
        # Retorna resultado
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0
        
        if has_errors:
            logger.warning(f"Validação falhou com {len(self.errors)} erro(s)")
        elif has_warnings:
            logger.info(f"Validação OK com {len(self.warnings)} aviso(s)")
        
        return not has_errors and (not strict or not has_warnings)
    
    def _validate_metadata(self, metadata: Dict[str, Any]):
        """Valida metadados da nota"""
        # Chave de acesso
        chave = metadata.get('chave_acesso', '')
        if chave and not self.CHAVE_NFE_PATTERN.match(chave):
            self.errors.append(f"Chave de acesso inválida: {chave}")
        
        # Número da nota
        numero = metadata.get('numero', '')
        if not numero or not str(numero).isdigit():
            self.errors.append("Número da nota ausente ou inválido")
        
        # Modelo
        modelo = metadata.get('modelo', '')
        if modelo not in self.VALID_MODELOS:
            self.warnings.append(f"Modelo não reconhecido: {modelo}")
        
        # Tipo de operação
        tipo_op = metadata.get('tipo_operacao', '')
        if tipo_op and tipo_op not in self.VALID_TIPOS_OPERACAO:
            self.warnings.append(f"Tipo de operação não reconhecido: {tipo_op}")
        
        # Data de emissão
        data_emissao = metadata.get('data_emissao')
        if not data_emissao:
            self.errors.append("Data de emissão ausente")
    
    def _validate_emitente(self, emitente: Dict[str, Any]):
        """Valida dados do emitente"""
        # CNPJ ou CPF obrigatório
        cnpj = emitente.get('cnpj', '')
        cpf = emitente.get('cpf', '')
        
        if not cnpj and not cpf:
            self.errors.append("Emitente sem CNPJ ou CPF")
        elif cnpj and not self.CNPJ_PATTERN.match(cnpj):
            self.errors.append(f"CNPJ do emitente inválido: {cnpj}")
        elif cpf and not self.CPF_PATTERN.match(cpf):
            self.errors.append(f"CPF do emitente inválido: {cpf}")
        
        # Razão social obrigatória
        razao = emitente.get('razao_social', '')
        if not razao or len(razao) < 3:
            self.errors.append("Razão social do emitente ausente ou inválida")
        
        # Inscrição estadual
        ie = emitente.get('inscricao_estadual', '')
        if not ie:
            self.warnings.append("Inscrição estadual do emitente ausente")
        
        # Endereço
        endereco = emitente.get('endereco', {})
        if not endereco.get('uf'):
            self.errors.append("UF do emitente ausente")
        if not endereco.get('municipio'):
            self.warnings.append("Município do emitente ausente")
    
    def _validate_destinatario(self, destinatario: Dict[str, Any]):
        """Valida dados do destinatário"""
        # CNPJ ou CPF (pode ser opcional em alguns casos)
        cnpj = destinatario.get('cnpj', '')
        cpf = destinatario.get('cpf', '')
        
        if cnpj and not self.CNPJ_PATTERN.match(cnpj):
            self.errors.append(f"CNPJ do destinatário inválido: {cnpj}")
        elif cpf and not self.CPF_PATTERN.match(cpf):
            self.errors.append(f"CPF do destinatário inválido: {cpf}")
        
        # Nome (pode ser consumidor final sem nome)
        nome = destinatario.get('razao_social', '')
        if not nome:
            self.warnings.append("Nome do destinatário ausente")
    
    def _validate_valores(self, valores: Dict[str, Any]):
        """Valida valores totais da nota"""
        valor_total = valores.get('valor_total', 0.0)
        valor_produtos = valores.get('valor_produtos', 0.0)
        
        # Valor total obrigatório
        if valor_total <= 0:
            self.errors.append("Valor total da nota deve ser maior que zero")
        
        # Valor produtos obrigatório
        if valor_produtos <= 0:
            self.errors.append("Valor dos produtos deve ser maior que zero")
        
        # Consistência básica: valor total >= valor produtos - desconto
        desconto = valores.get('valor_desconto', 0.0)
        frete = valores.get('valor_frete', 0.0)
        outros = valores.get('valor_outros', 0.0)
        
        valor_calculado = valor_produtos - desconto + frete + outros
        
        # Tolerância de 0.02 para arredondamentos
        diferenca = abs(valor_total - valor_calculado)
        if diferenca > 0.02:
            self.warnings.append(
                f"Divergência nos valores: Total={valor_total:.2f}, "
                f"Calculado={valor_calculado:.2f}, Diferença={diferenca:.2f}"
            )
        
        # Valores negativos
        if valor_produtos < 0:
            self.errors.append("Valor dos produtos não pode ser negativo")
        if desconto < 0:
            self.warnings.append("Valor do desconto não pode ser negativo")
    
    def _validate_itens(self, itens: List[Dict[str, Any]]):
        """Valida lista de itens da nota"""
        if not itens:
            self.errors.append("Nota fiscal sem itens")
            return
        
        for i, item in enumerate(itens, 1):
            produto = item.get('produto', {})
            
            # Código do produto
            codigo = produto.get('codigo', '')
            if not codigo:
                self.warnings.append(f"Item {i}: código do produto ausente")
            
            # Descrição
            descricao = produto.get('descricao', '')
            if not descricao or len(descricao) < 3:
                self.errors.append(f"Item {i}: descrição inválida ou ausente")
            
            # NCM
            ncm = produto.get('ncm', '')
            if not ncm:
                self.warnings.append(f"Item {i}: NCM ausente")
            elif not ncm.isdigit() or len(ncm) != 8:
                self.warnings.append(f"Item {i}: NCM inválido: {ncm}")
            
            # CFOP
            cfop = produto.get('cfop', '')
            if not cfop:
                self.warnings.append(f"Item {i}: CFOP ausente")
            elif not cfop.isdigit() or len(cfop) != 4:
                self.warnings.append(f"Item {i}: CFOP inválido: {cfop}")
            
            # Quantidade e valores
            qtd = produto.get('quantidade', 0.0)
            if qtd <= 0:
                self.errors.append(f"Item {i}: quantidade deve ser maior que zero")
            
            valor_unit = produto.get('valor_unitario', 0.0)
            if valor_unit <= 0:
                self.errors.append(f"Item {i}: valor unitário deve ser maior que zero")
            
            valor_total = produto.get('valor_total', 0.0)
            if valor_total <= 0:
                self.errors.append(f"Item {i}: valor total deve ser maior que zero")
            
            # Consistência: valor_total ≈ quantidade * valor_unitario
            if qtd > 0 and valor_unit > 0:
                valor_calc = qtd * valor_unit
                diferenca = abs(valor_total - valor_calc)
                
                # Tolerância de 0.02 por item
                if diferenca > 0.02:
                    self.warnings.append(
                        f"Item {i}: Divergência no valor total "
                        f"(Total={valor_total:.2f}, Calculado={valor_calc:.2f})"
                    )
    
    def _validate_consistency(self, data: Dict[str, Any]):
        """Valida consistência geral dos dados"""
        # Soma dos itens deve bater com valor total de produtos
        itens = data.get('itens', [])
        valores = data.get('valores', {})
        
        if itens:
            soma_itens = sum(
                item.get('produto', {}).get('valor_total', 0.0) 
                for item in itens
            )
            valor_produtos = valores.get('valor_produtos', 0.0)
            
            diferenca = abs(soma_itens - valor_produtos)
            if diferenca > 0.02:
                self.warnings.append(
                    f"Divergência: Soma itens={soma_itens:.2f}, "
                    f"Valor produtos={valor_produtos:.2f}"
                )
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Retorna relatório de validação
        
        Returns:
            Dicionário com erros, warnings e status
        """
        return {
            'is_valid': len(self.errors) == 0,
            'has_warnings': len(self.warnings) > 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
        }
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """
        Valida CNPJ (formato e dígitos verificadores)
        
        Args:
            cnpj: String com CNPJ (apenas números)
            
        Returns:
            True se válido
        """
        if not cnpj or len(cnpj) != 14 or not cnpj.isdigit():
            return False
        
        # Valida dígitos verificadores
        def calc_digit(cnpj_base: str, weights: List[int]) -> int:
            total = sum(int(d) * w for d, w in zip(cnpj_base, weights))
            resto = total % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit1 = calc_digit(cnpj[:12], weights1)
        
        if int(cnpj[12]) != digit1:
            return False
        
        # Segundo dígito
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit2 = calc_digit(cnpj[:13], weights2)
        
        return int(cnpj[13]) == digit2
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Valida CPF (formato e dígitos verificadores)
        
        Args:
            cpf: String com CPF (apenas números)
            
        Returns:
            True se válido
        """
        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return False
        
        # Verifica sequências inválidas (111.111.111-11, etc)
        if cpf == cpf[0] * 11:
            return False
        
        # Valida dígitos verificadores
        def calc_digit(cpf_base: str, multiplier: int) -> int:
            total = sum(int(d) * (multiplier - i) for i, d in enumerate(cpf_base))
            resto = total % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito
        digit1 = calc_digit(cpf[:9], 10)
        if int(cpf[9]) != digit1:
            return False
        
        # Segundo dígito
        digit2 = calc_digit(cpf[:10], 11)
        return int(cpf[10]) == digit2