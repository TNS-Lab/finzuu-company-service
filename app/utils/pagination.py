from typing import Union, Type
from beanie import Document
from app.schemas.response_schema import PaginateResponse


async def pagination(model: Union[Type[Document], int], limit: int, page: int) -> PaginateResponse:
    """
    Crée un objet de pagination pour une requête Beanie.
    
    Args:
        model: Un modèle Beanie Document ou un nombre total d'éléments
        limit: Nombre d'éléments par page (doit être > 0)
        page: Numéro de la page actuelle (commence à 1)
    
    Returns:
        PaginateResponse: Objet contenant les informations de pagination
        
    Raises:
        ValueError: Si limit <= 0 ou page < 1
    """

    # Validation des paramètres
    if limit <= 0:
        raise ValueError("Le paramètre 'limit' doit être supérieur à 0")
    if page < 1:
        raise ValueError("Le paramètre 'page' doit être supérieur ou égal à 1")
    
    # Déterminer le nombre total d'éléments
    if isinstance(model, int):
        total_items = model
    else:
        try:
            # Beanie utilise count_documents() au lieu de count()
            total_items = await model.count()
        except AttributeError:
            raise TypeError(
                "Le paramètre 'model' doit être un modèle Beanie Document "
                "avec une méthode count() ou un entier"
            )
        except Exception as e:
            raise RuntimeError(f"Erreur lors du comptage des éléments: {str(e)}")
    
    # Calculer le nombre total de pages
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    
    # S'assurer que la page demandée n'excède pas le total
    current_page = min(page, total_pages)
    
    return PaginateResponse(
        total=total_items,
        per_page=limit,
        current_page=current_page,
        last_page=total_pages
    )


def get_skip_value(page: int, limit: int) -> int:
    """
    Calcule la valeur de skip pour une pagination Beanie.
    
    Args:
        page: Numéro de la page (commence à 1)
        limit: Nombre d'éléments par page
    
    Returns:
        int: Nombre d'éléments à sauter
    """
    return (page - 1) * limit


async def paginate_query(query, limit: int, page: int) -> tuple[list[Document], PaginateResponse]:
    """
    Exécute une requête Beanie avec pagination.
    
    Args:
        query: Une requête Beanie (ex: Message.find(Message.status == "active"))
        limit: Nombre d'éléments par page
        page: Numéro de la page actuelle
    
    Returns:
        tuple: (liste des documents, objet de pagination)
        
    Example:
        messages, paginator = await paginate_query(
            Message.find(Message.status == "active"),
            limit=10,
            page=1
        )
    """

    # Validation
    if limit <= 0:
        raise ValueError("Le paramètre 'limit' doit être supérieur à 0")
    if page < 1:
        raise ValueError("Le paramètre 'page' doit être supérieur ou égal à 1")
    
    # Compter le total
    total_items = await query.count()
    
    # Calculer skip et exécuter la requête
    skip = get_skip_value(page, limit)
    documents = await query.skip(skip).limit(limit).to_list()
    
    # Créer la pagination
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    current_page = min(page, total_pages)
    
    paginator = PaginateResponse(
        total=total_items,
        per_page=limit,
        current_page=current_page,
        last_page=total_pages
    )
    
    return documents, paginator
