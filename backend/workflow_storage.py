#!/usr/bin/env python3
"""
Sistema de armazenamento de workflows
Gerencia salvamento, carregamento e histórico de workflows
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid

from models import FlowData

class WorkflowMetadata(BaseModel):
    """Metadados de um workflow salvo"""
    id: str
    name: str
    description: str = ""
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    tags: List[str] = []
    author: str = "user"
    is_template: bool = False

class SavedWorkflow(BaseModel):
    """Workflow salvo completo"""
    metadata: WorkflowMetadata
    flow_data: FlowData
    file_path: str

class WorkflowStorage:
    """Gerenciador de armazenamento de workflows"""
    
    def __init__(self, storage_dir: str = "workflows"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Subdiretórios
        self.workflows_dir = self.storage_dir / "saved"
        self.templates_dir = self.storage_dir / "templates"
        self.backups_dir = self.storage_dir / "backups"
        
        for dir_path in [self.workflows_dir, self.templates_dir, self.backups_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def save_workflow(
        self, 
        flow_data: FlowData, 
        name: str,
        description: str = "",
        tags: List[str] = None,
        is_template: bool = False,
        workflow_id: str = None
    ) -> SavedWorkflow:
        """Salva um workflow"""
        
        # Gerar ID se não fornecido
        if not workflow_id:
            workflow_id = str(uuid.uuid4())
        
        # Criar metadados
        now = datetime.now()
        metadata = WorkflowMetadata(
            id=workflow_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            tags=tags or [],
            is_template=is_template
        )
        
        # Determinar diretório e nome do arquivo
        target_dir = self.templates_dir if is_template else self.workflows_dir
        safe_name = self._sanitize_filename(name)
        file_name = f"{safe_name}_{workflow_id[:8]}.json"
        file_path = target_dir / file_name
        
        # Criar workflow salvo
        saved_workflow = SavedWorkflow(
            metadata=metadata,
            flow_data=flow_data,
            file_path=str(file_path)
        )
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(saved_workflow.dict(), f, indent=2, ensure_ascii=False, default=str)
        
        return saved_workflow
    
    def load_workflow(self, workflow_id: str) -> Optional[SavedWorkflow]:
        """Carrega um workflow pelo ID"""
        
        # Procurar em workflows e templates
        for search_dir in [self.workflows_dir, self.templates_dir]:
            for file_path in search_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get('metadata', {}).get('id') == workflow_id:
                        return SavedWorkflow(**data)
                        
                except Exception as e:
                    print(f"Erro ao carregar {file_path}: {e}")
                    continue
        
        return None
    
    def list_workflows(self, include_templates: bool = True) -> List[WorkflowMetadata]:
        """Lista todos os workflows salvos"""
        workflows = []
        
        # Listar workflows normais
        workflows.extend(self._list_workflows_in_dir(self.workflows_dir))
        
        # Listar templates se solicitado
        if include_templates:
            workflows.extend(self._list_workflows_in_dir(self.templates_dir))
        
        # Ordenar por data de atualização (mais recente primeiro)
        workflows.sort(key=lambda w: w.updated_at, reverse=True)
        
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Deleta um workflow"""
        
        # Procurar e deletar
        for search_dir in [self.workflows_dir, self.templates_dir]:
            for file_path in search_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get('metadata', {}).get('id') == workflow_id:
                        # Fazer backup antes de deletar
                        self._backup_workflow(file_path)
                        file_path.unlink()
                        return True
                        
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")
                    continue
        
        return False
    
    def update_workflow(
        self, 
        workflow_id: str, 
        flow_data: FlowData = None,
        name: str = None,
        description: str = None,
        tags: List[str] = None
    ) -> Optional[SavedWorkflow]:
        """Atualiza um workflow existente"""
        
        # Carregar workflow atual
        current_workflow = self.load_workflow(workflow_id)
        if not current_workflow:
            return None
        
        # Fazer backup
        self._backup_workflow(Path(current_workflow.file_path))
        
        # Atualizar dados
        if flow_data:
            current_workflow.flow_data = flow_data
        
        if name:
            current_workflow.metadata.name = name
        
        if description is not None:
            current_workflow.metadata.description = description
        
        if tags is not None:
            current_workflow.metadata.tags = tags
        
        current_workflow.metadata.updated_at = datetime.now()
        
        # Salvar arquivo atualizado
        with open(current_workflow.file_path, 'w', encoding='utf-8') as f:
            json.dump(current_workflow.dict(), f, indent=2, ensure_ascii=False, default=str)
        
        return current_workflow
    
    def search_workflows(self, query: str, tags: List[str] = None) -> List[WorkflowMetadata]:
        """Busca workflows por nome, descrição ou tags"""
        all_workflows = self.list_workflows()
        results = []
        
        query_lower = query.lower() if query else ""
        
        for workflow in all_workflows:
            # Buscar por nome ou descrição
            if query_lower:
                if (query_lower in workflow.name.lower() or 
                    query_lower in workflow.description.lower()):
                    results.append(workflow)
                    continue
            
            # Buscar por tags
            if tags:
                if any(tag in workflow.tags for tag in tags):
                    results.append(workflow)
                    continue
            
            # Se não há query nem tags, incluir todos
            if not query_lower and not tags:
                results.append(workflow)
        
        return results
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos workflows"""
        try:
            workflows = self.list_workflows()
            templates = [w for w in workflows if w.is_template]
            regular = [w for w in workflows if not w.is_template]
            
            # Contar por tags
            tag_counts = {}
            for workflow in workflows:
                for tag in workflow.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Calcular datas mais antigas e mais novas
            oldest_workflow = None
            newest_workflow = None
            
            if workflows:
                try:
                    oldest_workflow = min(workflows, key=lambda w: w.created_at).created_at
                    newest_workflow = max(workflows, key=lambda w: w.created_at).created_at
                except Exception:
                    # Se houver erro na comparação de datas, ignorar
                    pass
            
            return {
                "total_workflows": len(workflows),
                "regular_workflows": len(regular),
                "templates": len(templates),
                "most_used_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "storage_size_mb": self._get_storage_size_mb(),
                "oldest_workflow": oldest_workflow,
                "newest_workflow": newest_workflow
            }
            
        except Exception as e:
            # Retornar stats vazias em caso de erro
            return {
                "total_workflows": 0,
                "regular_workflows": 0,
                "templates": 0,
                "most_used_tags": [],
                "storage_size_mb": 0.0,
                "oldest_workflow": None,
                "newest_workflow": None
            }
    
    def _list_workflows_in_dir(self, directory: Path) -> List[WorkflowMetadata]:
        """Lista workflows em um diretório específico"""
        workflows = []
        
        for file_path in directory.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = WorkflowMetadata(**data['metadata'])
                workflows.append(metadata)
                
            except Exception as e:
                print(f"Erro ao carregar metadados de {file_path}: {e}")
                continue
        
        return workflows
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitiza nome para uso como nome de arquivo"""
        # Remover caracteres inválidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limitar tamanho
        return name[:50]
    
    def _backup_workflow(self, file_path: Path):
        """Faz backup de um workflow antes de modificar/deletar"""
        if not file_path.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backups_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")
    
    def _get_storage_size_mb(self) -> float:
        """Calcula tamanho total do armazenamento em MB"""
        total_size = 0
        
        for file_path in self.storage_dir.rglob("*.json"):
            try:
                total_size += file_path.stat().st_size
            except:
                continue
        
        return round(total_size / (1024 * 1024), 2)

# Instância global
workflow_storage = WorkflowStorage()