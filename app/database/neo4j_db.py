from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from app.config import get_settings

settings = get_settings()


class Neo4jDB:
    driver = None
    connected = False


neo4j_db = Neo4jDB()


async def connect_neo4j():
    """Connect to Neo4j - graceful failure if not available"""
    try:
        neo4j_db.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        # Verify connectivity
        async with neo4j_db.driver.session() as session:
            await session.run("RETURN 1")
        neo4j_db.connected = True
        print(f"✅ Connected to Neo4j: {settings.neo4j_uri}")
    except ServiceUnavailable:
        print(f"⚠️  Neo4j not available at {settings.neo4j_uri} - Social features will be disabled")
        print("   To enable Neo4j, start it with: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
        neo4j_db.connected = False
    except AuthError:
        print(f"⚠️  Neo4j authentication failed - check NEO4J_USER and NEO4J_PASSWORD in .env")
        neo4j_db.connected = False
    except Exception as e:
        print(f"⚠️  Neo4j connection error: {e}")
        neo4j_db.connected = False


async def close_neo4j():
    """Close Neo4j connection"""
    if neo4j_db.driver and neo4j_db.connected:
        await neo4j_db.driver.close()
        print("Neo4j connection closed")


def get_neo4j_driver():
    """Get Neo4j driver instance"""
    return neo4j_db.driver


def is_neo4j_connected():
    """Check if Neo4j is connected"""
    return neo4j_db.connected
