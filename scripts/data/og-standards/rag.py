#!/usr/bin/env python3
"""
ABOUTME: O&G Standards RAG Query Interface
ABOUTME: Semantic search with AI-powered answers using Claude or OpenAI

Usage:
    python rag.py "What are the requirements for riser design in API RP 2RD?"
    python rag.py --interactive
"""

import argparse
import logging
import os
import pickle
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def get_query_embedding_openai(query: str, model: str = "text-embedding-3-small") -> List[float]:
    """Get embedding for query using OpenAI."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("OpenAI not installed")
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(model=model, input=[query])
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        return []


def get_query_embedding_local(query: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    """Get embedding for query using local model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.error("sentence-transformers not installed")
        return []

    try:
        model = SentenceTransformer(model_name)
        embedding = model.encode([query])[0]
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Local embedding error: {e}")
        return []


def get_ai_response_claude(query: str, context: str) -> str:
    """Get AI response using Claude."""
    try:
        import anthropic
    except ImportError:
        return "[Claude API not available - install anthropic package]"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "[ANTHROPIC_API_KEY not set]"

    try:
        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = """You are an expert O&G (Oil & Gas) engineering assistant with deep knowledge of industry standards including API, DNV, ASTM, ISO, Norsok, and others.

Your role is to:
1. Answer technical questions using the provided context from O&G standards documents
2. Cite specific standards when providing information
3. Be precise and technically accurate
4. Acknowledge when information is not available in the context

Always format your response clearly with:
- Direct answer to the question
- Relevant citations from the standards
- Any caveats or additional considerations"""

        user_message = f"""Based on the following excerpts from O&G standards documents, please answer this question:

**Question:** {query}

**Relevant Standards Context:**
{context}

Please provide a comprehensive answer based on the above context."""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        return response.content[0].text

    except Exception as e:
        return f"[Claude API error: {e}]"


def get_ai_response_openai(query: str, context: str) -> str:
    """Get AI response using OpenAI."""
    try:
        from openai import OpenAI
    except ImportError:
        return "[OpenAI API not available - install openai package]"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[OPENAI_API_KEY not set]"

    try:
        client = OpenAI(api_key=api_key)

        system_prompt = """You are an expert O&G (Oil & Gas) engineering assistant with deep knowledge of industry standards including API, DNV, ASTM, ISO, Norsok, and others.

Your role is to:
1. Answer technical questions using the provided context from O&G standards documents
2. Cite specific standards when providing information
3. Be precise and technically accurate
4. Acknowledge when information is not available in the context"""

        user_message = f"""Based on the following excerpts from O&G standards documents, please answer this question:

**Question:** {query}

**Relevant Standards Context:**
{context}

Please provide a comprehensive answer based on the above context."""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[OpenAI API error: {e}]"


class RAGQueryEngine:
    """RAG-based query engine for O&G standards."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database_path']
        self.conn = None
        self.embeddings_cache = {}

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def connect(self):
        """Connect to database."""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row

    def load_embeddings(self) -> int:
        """Load all embeddings into memory for fast search."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT tc.id, tc.document_id, tc.chunk_num, tc.chunk_text,
                   tc.embedding, tc.embedding_model,
                   d.filename, d.organization, d.doc_type, d.doc_number
            FROM text_chunks tc
            JOIN documents d ON tc.document_id = d.id
            WHERE tc.embedding IS NOT NULL
        ''')

        count = 0
        for row in cursor.fetchall():
            embedding = pickle.loads(row['embedding'])
            self.embeddings_cache[row['id']] = {
                'id': row['id'],
                'document_id': row['document_id'],
                'chunk_num': row['chunk_num'],
                'chunk_text': row['chunk_text'],
                'embedding': embedding,
                'model': row['embedding_model'],
                'filename': row['filename'],
                'organization': row['organization'],
                'doc_type': row['doc_type'],
                'doc_number': row['doc_number']
            }
            count += 1

        return count

    def semantic_search(self, query: str, top_k: int = 5,
                        embedding_model: str = "local") -> List[dict]:
        """
        Perform semantic search using embeddings.

        Args:
            query: Search query
            top_k: Number of results to return
            embedding_model: 'openai' or 'local'

        Returns:
            List of matching chunks with scores
        """
        # Get query embedding
        if embedding_model == "openai":
            query_embedding = get_query_embedding_openai(query)
        else:
            query_embedding = get_query_embedding_local(query)

        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []

        # Calculate similarities
        results = []
        for chunk_id, chunk_data in self.embeddings_cache.items():
            similarity = cosine_similarity(query_embedding, chunk_data['embedding'])
            results.append({
                **chunk_data,
                'score': similarity
            })

        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def keyword_search(self, query: str, limit: int = 10) -> List[dict]:
        """
        Fallback keyword search using FTS5.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching chunks
        """
        cursor = self.conn.cursor()

        # Try FTS search first
        try:
            cursor.execute('''
                SELECT tc.id, tc.document_id, tc.chunk_num, tc.chunk_text,
                       d.filename, d.organization, d.doc_type, d.doc_number
                FROM text_chunks tc
                JOIN documents d ON tc.document_id = d.id
                WHERE tc.chunk_text LIKE ?
                ORDER BY d.organization, d.filename
                LIMIT ?
            ''', (f'%{query}%', limit))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []

    def build_context(self, results: List[dict], max_chars: int = 8000) -> str:
        """Build context string from search results."""
        context_parts = []
        total_chars = 0

        for r in results:
            # Build citation
            citation = f"{r.get('organization', 'Unknown')}"
            if r.get('doc_type'):
                citation += f" {r['doc_type']}"
            if r.get('doc_number'):
                citation += f" {r['doc_number']}"

            chunk_text = r.get('chunk_text', '')
            score = r.get('score', 0)

            # Format context entry
            entry = f"**Source: {citation}** (Relevance: {score:.2f})\n{chunk_text}\n"

            if total_chars + len(entry) > max_chars:
                break

            context_parts.append(entry)
            total_chars += len(entry)

        return "\n---\n".join(context_parts)

    def query(self, question: str, top_k: int = 5,
              ai_model: str = "claude",
              embedding_model: str = "local",
              show_sources: bool = True) -> Tuple[str, List[dict]]:
        """
        Process a RAG query.

        Args:
            question: User's question
            top_k: Number of context chunks
            ai_model: 'claude' or 'openai' for answer generation
            embedding_model: 'local' or 'openai' for embeddings
            show_sources: Whether to include source information

        Returns:
            Tuple of (answer, sources)
        """
        # Load embeddings if not cached
        if not self.embeddings_cache:
            count = self.load_embeddings()
            if count == 0:
                # Fall back to keyword search
                results = self.keyword_search(question, limit=top_k)
                if not results:
                    return "No relevant documents found. Please run embed.py first to enable semantic search.", []
            else:
                results = self.semantic_search(question, top_k, embedding_model)
        else:
            results = self.semantic_search(question, top_k, embedding_model)

        if not results:
            return "No relevant documents found for your query.", []

        # Build context
        context = self.build_context(results)

        # Get AI response
        if ai_model == "claude":
            answer = get_ai_response_claude(question, context)
        else:
            answer = get_ai_response_openai(question, context)

        return answer, results

    def interactive_mode(self, ai_model: str = "claude",
                         embedding_model: str = "local"):
        """Run interactive query mode."""
        print("\n" + "=" * 60)
        print("O&G STANDARDS AI ASSISTANT")
        print("=" * 60)
        print("Ask questions about O&G standards. Type 'quit' to exit.")
        print("=" * 60 + "\n")

        # Load embeddings
        count = self.load_embeddings()
        print(f"Loaded {count:,} document chunks for semantic search.\n")

        while True:
            try:
                question = input("\n🔍 Your question: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not question:
                    continue

                print("\n⏳ Searching and generating answer...")

                answer, sources = self.query(
                    question,
                    top_k=5,
                    ai_model=ai_model,
                    embedding_model=embedding_model
                )

                print("\n" + "=" * 60)
                print("📖 ANSWER")
                print("=" * 60)
                print(answer)

                if sources:
                    print("\n" + "-" * 60)
                    print("📚 SOURCES")
                    print("-" * 60)
                    for i, s in enumerate(sources[:5], 1):
                        org = s.get('organization', 'Unknown')
                        doc_type = s.get('doc_type', '')
                        doc_num = s.get('doc_number', '')
                        filename = s.get('filename', '')
                        score = s.get('score', 0)

                        ref = f"{org}"
                        if doc_type:
                            ref += f" {doc_type}"
                        if doc_num:
                            ref += f" {doc_num}"

                        print(f"{i}. [{ref}] {filename[:50]} (score: {score:.3f})")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='RAG Query Interface for O&G Standards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "What are API requirements for riser design?"
  %(prog)s --interactive
  %(prog)s --ai openai "DNV fatigue assessment methods"
  %(prog)s --no-sources "ASTM A320 bolt grades"
        """
    )
    parser.add_argument(
        'question',
        nargs='?',
        help='Question to ask about O&G standards'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--ai',
        choices=['claude', 'openai'],
        default='claude',
        help='AI model for answer generation (default: claude)'
    )
    parser.add_argument(
        '--embedding',
        choices=['local', 'openai'],
        default='local',
        help='Embedding model type (default: local)'
    )
    parser.add_argument(
        '--top-k', '-k',
        type=int,
        default=5,
        help='Number of context chunks (default: 5)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--no-sources',
        action='store_true',
        help='Hide source citations'
    )

    args = parser.parse_args()

    # Find config file
    config_path = args.config
    if not os.path.isabs(config_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_path)

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    # Create engine
    engine = RAGQueryEngine(config_path)

    try:
        engine.connect()

        if args.interactive:
            engine.interactive_mode(
                ai_model=args.ai,
                embedding_model=args.embedding
            )
        elif args.question:
            answer, sources = engine.query(
                args.question,
                top_k=args.top_k,
                ai_model=args.ai,
                embedding_model=args.embedding
            )

            print("\n" + "=" * 60)
            print("ANSWER")
            print("=" * 60)
            print(answer)

            if sources and not args.no_sources:
                print("\n" + "-" * 60)
                print("SOURCES")
                print("-" * 60)
                for i, s in enumerate(sources[:5], 1):
                    org = s.get('organization', 'Unknown')
                    doc_type = s.get('doc_type', '')
                    doc_num = s.get('doc_number', '')
                    filename = s.get('filename', '')
                    score = s.get('score', 0)

                    ref = f"{org}"
                    if doc_type:
                        ref += f" {doc_type}"
                    if doc_num:
                        ref += f" {doc_num}"

                    print(f"{i}. [{ref}] {filename[:50]} (score: {score:.3f})")
        else:
            parser.print_help()

    finally:
        engine.close()


if __name__ == '__main__':
    main()
