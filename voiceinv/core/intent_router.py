"""
Intent Router Module

Routes parsed intents to appropriate inventory operations.
Handles security checks and command confirmation for destructive operations.
"""

from typing import Dict, Any
from utils.logger import get_logger
from core.inventory_engine import InventoryEngine


class IntentRouterError(Exception):
    """Exception for intent routing errors."""
    pass


class IntentRouter:
    """
    Routes intents to appropriate handlers with security checks.
    """

    def __init__(self, inventory_engine: InventoryEngine, config: Dict[str, Any]):
        """
        Initialize intent router.

        Args:
            inventory_engine: Inventory engine instance
            config: Security configuration
        """
        self.inventory_engine = inventory_engine
        self.config = config
        self.logger = get_logger(__name__)

        # Security settings
        self.confirm_destructive = config.get('confirm_destructive_operations', True)
        self.max_delete_without_confirm = config.get('max_delete_items_without_confirm', 10)

        # Intent handlers
        self.handlers = {
            'add_item': self._handle_add_item,
            'update_stock': self._handle_update_stock,
            'remove_item': self._handle_remove_item,
            'query': self._handle_query,
            'report': self._handle_report,
        }

        self.logger.info("Intent Router initialized")

    def route(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route parsed command to appropriate handler.

        Args:
            parse_result: Result from NLP parser

        Returns:
            Execution result dictionary
        """
        result = {
            'success': False,
            'intent': parse_result.get('intent'),
            'data': None,
            'error': None
        }

        try:
            intent = parse_result.get('intent')
            entities = parse_result.get('entities', {})

            if intent not in self.handlers:
                result['error'] = f"Unknown intent: {intent}"
                return result

            # Call appropriate handler
            handler = self.handlers[intent]
            handler_result = handler(entities)

            result.update(handler_result)

            return result

        except Exception as e:
            self.logger.error(f"Error routing intent: {e}", exc_info=True)
            result['error'] = str(e)
            return result

    def _handle_add_item(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_item intent."""
        try:
            item_name = entities['item_name']
            quantity = entities.get('quantity', 1)
            price = entities.get('price')
            category = entities.get('category')

            self.logger.info(f"Adding item: {item_name}, qty: {quantity}, price: {price}")

            # Add item to inventory
            item_id = self.inventory_engine.add_item(
                name=item_name,
                quantity=quantity,
                unit_price=price,
                category=category
            )

            return {
                'success': True,
                'data': {
                    'item_id': item_id,
                    'item_name': item_name,
                    'quantity': quantity,
                    'price': price
                }
            }

        except Exception as e:
            self.logger.error(f"Error adding item: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_update_stock(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_stock intent."""
        try:
            item_name = entities['item_name']
            quantity_change = entities['quantity_change']

            self.logger.info(f"Updating stock: {item_name}, change: {quantity_change}")

            # Update stock
            new_quantity = self.inventory_engine.update_stock(
                item_name=item_name,
                quantity_change=quantity_change
            )

            return {
                'success': True,
                'data': {
                    'item_name': item_name,
                    'quantity_change': quantity_change,
                    'new_quantity': new_quantity
                }
            }

        except Exception as e:
            self.logger.error(f"Error updating stock: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_remove_item(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle remove_item intent."""
        try:
            item_name = entities['item_name']
            quantity = entities.get('quantity')

            if quantity:
                # Remove specific quantity
                self.logger.info(f"Removing quantity: {item_name}, qty: {quantity}")
                new_quantity = self.inventory_engine.update_stock(
                    item_name=item_name,
                    quantity_change=-quantity
                )

                return {
                    'success': True,
                    'data': {
                        'item_name': item_name,
                        'quantity_removed': quantity,
                        'new_quantity': new_quantity
                    }
                }
            else:
                # Remove item completely
                self.logger.info(f"Removing item: {item_name}")
                self.inventory_engine.remove_item(item_name=item_name)

                return {
                    'success': True,
                    'data': {
                        'item_name': item_name,
                        'removed_completely': True
                    }
                }

        except Exception as e:
            self.logger.error(f"Error removing item: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_query(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query intent."""
        try:
            query_type = entities.get('query_type', 'single')

            if query_type == 'all':
                # Get all items
                self.logger.info("Querying all items")
                items = self.inventory_engine.get_all_items()

                return {
                    'success': True,
                    'data': {
                        'query_type': 'all',
                        'items': items,
                        'total_items': len(items)
                    }
                }
            else:
                # Get specific item
                item_name = entities['item_name']
                self.logger.info(f"Querying item: {item_name}")

                item = self.inventory_engine.get_item(item_name=item_name)

                return {
                    'success': True,
                    'data': {
                        'query_type': 'single',
                        'item': item
                    }
                }

        except Exception as e:
            self.logger.error(f"Error querying: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_report(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report intent."""
        try:
            report_type = entities.get('report_type', 'summary')

            self.logger.info(f"Generating report: {report_type}")

            # Generate report
            report_data = self.inventory_engine.generate_report(report_type=report_type)

            return {
                'success': True,
                'data': {
                    'report_type': report_type,
                    'report': report_data
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return {'success': False, 'error': str(e)}
