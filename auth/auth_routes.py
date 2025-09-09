# auth/auth_routes.py
"""
Flask routes for handling Google OAuth authentication
Integrates with Dash application for seamless login/logout
"""

from flask import Flask, request, redirect, session, jsonify, make_response
from urllib.parse import urlencode, parse_qs
import os
import json
from datetime import datetime, timedelta
from .google_auth import GoogleOAuthManager, UserManager, SessionManager

def register_auth_routes(server: Flask):
    """Register authentication routes with Flask server"""
    
    oauth_manager = GoogleOAuthManager(server)
    user_manager = UserManager()
    session_manager = SessionManager()
    
    @server.route('/auth/login')
    def login():
        """Initiate Google OAuth login flow"""
        try:
            # Generate state for CSRF protection
            state = session.get('oauth_state') or os.urandom(16).hex()
            session['oauth_state'] = state
            
            # Get OAuth URL and redirect
            auth_url = oauth_manager.get_auth_url(state)
            return redirect(auth_url)
            
        except Exception as e:
            print(f"❌ Login initiation failed: {e}")
            return redirect('/?error=login_failed')
    
    @server.route('/auth/google-callback')
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            # Verify state parameter (CSRF protection)
            state = request.args.get('state')
            if state != session.get('oauth_state'):
                print("❌ Invalid OAuth state parameter")
                return redirect('/?error=invalid_state')
            
            # Get authorization code
            code = request.args.get('code')
            if not code:
                error = request.args.get('error', 'unknown_error')
                print(f"❌ OAuth callback error: {error}")
                return redirect(f'/?error=oauth_{error}')
            
            # Exchange code for token
            token_data = oauth_manager.exchange_code_for_token(code)
            if not token_data:
                print("❌ Failed to exchange authorization code")
                return redirect('/?error=token_exchange_failed')
            
            # Get user information
            user_info = oauth_manager.get_user_info(token_data['access_token'])
            if not user_info:
                print("❌ Failed to get user information")
                return redirect('/?error=user_info_failed')
            
            # Create or update user in database
            user = user_manager.get_or_create_user(user_info)
            if not user:
                print("❌ Failed to create/update user")
                return redirect('/?error=user_creation_failed')
            
            # Create session
            session_token = session_manager.create_session(user['id'])
            if not session_token:
                print("❌ Failed to create session")
                return redirect('/?error=session_creation_failed')
            
            # Clear OAuth state
            session.pop('oauth_state', None)
            
            # Create response with session cookie
            response = make_response(redirect('/?login=success'))
            
            # Set secure session cookie
            response.set_cookie(
                'usc_ir_session',
                session_token,
                max_age=8*3600,  # 8 hours
                httponly=True,
                secure=not server.debug,  # Use secure cookies in production
                samesite='Lax'
            )
            
            print(f"✅ User logged in successfully: {user['email']}")
            return response
            
        except Exception as e:
            print(f"❌ OAuth callback error: {e}")
            return redirect('/?error=callback_failed')
    
    @server.route('/auth/logout', methods=['POST'])
    def logout():
        """Handle user logout"""
        try:
            session_token = request.cookies.get('usc_ir_session')
            
            if session_token:
                # Invalidate session in database
                session_manager.invalidate_session(session_token)
            
            # Create response and clear cookie
            response = make_response(redirect('/?logout=success'))
            response.set_cookie(
                'usc_ir_session',
                '',
                expires=0,
                httponly=True,
                secure=not server.debug,
                samesite='Lax'
            )
            
            print("✅ User logged out successfully")
            return response
            
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return redirect('/?error=logout_failed')
    
    @server.route('/auth/status')
    def auth_status():
        """Get current authentication status (API endpoint)"""
        try:
            session_token = request.cookies.get('usc_ir_session')
            
            if not session_token:
                return jsonify({
                    'authenticated': False,
                    'user': None,
                    'access_tier': 1
                })
            
            # Validate session
            user = session_manager.validate_session(session_token)
            
            if not user:
                # Invalid session, clear cookie
                response = make_response(jsonify({
                    'authenticated': False,
                    'user': None,
                    'access_tier': 1,
                    'session_expired': True
                }))
                response.set_cookie(
                    'usc_ir_session',
                    '',
                    expires=0,
                    httponly=True,
                    secure=not server.debug,
                    samesite='Lax'
                )
                return response
            
            # Return user info (excluding sensitive data)
            user_data = {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role'],
                'access_tier': user['access_tier'],
                'profile_picture': user['profile_picture']
            }
            
            return jsonify({
                'authenticated': True,
                'user': user_data,
                'access_tier': user['access_tier']
            })
            
        except Exception as e:
            print(f"❌ Auth status error: {e}")
            return jsonify({
                'authenticated': False,
                'user': None,
                'access_tier': 1,
                'error': 'status_check_failed'
            })
    
    @server.route('/auth/request-access', methods=['POST'])
    def request_access():
        """Handle access tier upgrade requests"""
        try:
            session_token = request.cookies.get('usc_ir_session')
            
            if not session_token:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Validate session
            user = session_manager.validate_session(session_token)
            if not user:
                return jsonify({'error': 'Invalid session'}), 401
            
            # Get request data
            data = request.get_json()
            requested_tier = data.get('requested_tier')
            justification = data.get('justification', '')
            
            if not requested_tier or requested_tier <= user['access_tier']:
                return jsonify({'error': 'Invalid access tier request'}), 400
            
            if requested_tier >= 3 and not justification.strip():
                return jsonify({'error': 'Justification required for financial access'}), 400
            
            # Store access request in database
            conn = sqlite3.connect('usc_ir.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO access_requests (user_id, requested_tier, justification)
                    VALUES (?, ?, ?)
                ''', (user['id'], requested_tier, justification))
                
                conn.commit()
                request_id = cursor.lastrowid
                
                print(f"📋 Access request submitted: User {user['email']} requests tier {requested_tier}")
                
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'message': 'Access request submitted successfully'
                })
                
            except sqlite3.Error as e:
                print(f"❌ Access request database error: {e}")
                return jsonify({'error': 'Failed to submit request'}), 500
            finally:
                conn.close()
            
        except Exception as e:
            print(f"❌ Access request error: {e}")
            return jsonify({'error': 'Request processing failed'}), 500
    
    @server.route('/auth/admin/pending-requests')
    def get_pending_requests():
        """Get pending access requests (admin only)"""
        try:
            session_token = request.cookies.get('usc_ir_session')
            
            if not session_token:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Validate session and check admin access
            user = session_manager.validate_session(session_token)
            if not user or user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            # Get pending requests
            conn = sqlite3.connect('usc_ir.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    SELECT ar.*, u.email, u.full_name
                    FROM access_requests ar
                    JOIN users u ON ar.user_id = u.id
                    WHERE ar.status = 'pending'
                    ORDER BY ar.requested_at DESC
                ''')
                
                requests = [dict(row) for row in cursor.fetchall()]
                
                return jsonify({
                    'success': True,
                    'requests': requests
                })
                
            except sqlite3.Error as e:
                print(f"❌ Failed to get pending requests: {e}")
                return jsonify({'error': 'Database error'}), 500
            finally:
                conn.close()
            
        except Exception as e:
            print(f"❌ Get pending requests error: {e}")
            return jsonify({'error': 'Request processing failed'}), 500
    
    print("✅ Authentication routes registered successfully")

# Utility function to get current user from request
def get_current_user():
    """Get current authenticated user from request context"""
    from flask import request, current_app
    
    session_token = request.cookies.get('usc_ir_session')
    if not session_token:
        return None
    
    session_manager = SessionManager()
    return session_manager.validate_session(session_token)