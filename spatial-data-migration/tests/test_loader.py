# tests/test_loader.py
import pytest
from unittest.mock import Mock, patch
from spatial_migration.core.loader import AWSLoader

def test_load_to_aws(sample_config):
    """Prueba la carga de datos a AWS"""
    with patch('boto3.client') as mock_boto3:
        mock_s3 = Mock()
        mock_glue = Mock()
        mock_boto3.side_effect = [mock_s3, mock_glue]
        
        loader = AWSLoader(sample_config.aws)
        result = loader.load_to_aws(
            Mock(),  # mock parquet_data
            'test_table',
            {'id': 'int64', 'name': 'object', 'geometry': 'object'}
        )
        
        assert result is True
        mock_s3.upload_fileobj.assert_called_once()
        mock_glue.create_table.assert_called_once()

def test_load_to_aws_s3_error(sample_config):
    """Prueba el manejo de errores de S3"""
    with patch('boto3.client') as mock_boto3:
        mock_s3 = Mock()
        mock_s3.upload_fileobj.side_effect = Exception("S3 Error")
        mock_boto3.return_value = mock_s3
        
        loader = AWSLoader(sample_config.aws)
        
        with pytest.raises(Exception) as exc_info:
            loader.load_to_aws(Mock(), 'test_table', {})
        
        assert "S3 Error" in str(exc_info.value)
