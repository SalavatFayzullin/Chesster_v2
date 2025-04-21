/**
 * Chess Board Alignment Fix
 * This script ensures proper alignment of the chessboard and its child elements
 */
document.addEventListener('DOMContentLoaded', function() {
    // Run the fix multiple times to ensure it catches delayed initialization
    setTimeout(fixChessboardAlignment, 100);
    setTimeout(fixChessboardAlignment, 500);
    setTimeout(fixChessboardAlignment, 1000);
    
    // Function to fix chessboard alignment
    function fixChessboardAlignment() {
        let chessboard = document.getElementById('chessboard');
        if (!chessboard) return;
        
        // Check if the board has been properly initialized
        if (window.board === null || typeof window.board === 'undefined') {
            console.log('Board not initialized yet, will retry later');
            return;
        }
        
        // Force board redraw/resize
        if (typeof window.board.resize === 'function') {
            window.board.resize();
        }
        
        // Add specific CSS class to fix chessboard
        chessboard.classList.add('fixed-chessboard');
        
        // More comprehensive fix for all elements
        let style = document.createElement('style');
        style.innerHTML = `
            .fixed-chessboard {
                width: 100% !important;
                margin: 0 auto !important;
                box-sizing: border-box !important;
                position: relative !important;
                display: block !important;
            }
            .fixed-chessboard > div {
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
                height: 100% !important;
                box-sizing: border-box !important;
                position: relative !important;
            }
            .square-55d63 {
                width: 12.5% !important;
                height: 0 !important;
                padding-bottom: 12.5% !important;
                float: left !important;
                position: relative !important;
            }
            .piece-417db {
                position: absolute !important;
                width: 100% !important;
                height: 100% !important;
                background-size: contain !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
            }
        `;
        
        // Avoid adding duplicate styles
        let existingStyle = document.querySelector('style[data-chess-fix="true"]');
        if (!existingStyle) {
            style.setAttribute('data-chess-fix', 'true');
            document.head.appendChild(style);
        }
        
        // Add mouse events for highlighting 
        setupDragEvents();
    }
    
    // Function to add dragging events
    function setupDragEvents() {
        // Add mousedown event to all pieces
        let pieces = document.querySelectorAll('.piece-417db');
        pieces.forEach(function(piece) {
            piece.addEventListener('mousedown', function() {
                document.body.classList.add('dragging-piece');
            });
        });
        
        // Add mouseup event to document
        document.addEventListener('mouseup', function() {
            document.body.classList.remove('dragging-piece');
        });
    }
    
    // Run the fix on window resize as well
    window.addEventListener('resize', fixChessboardAlignment);
    
    // Add a global fix that can be called from game.html
    window.fixChessboard = fixChessboardAlignment;
    
    // Add function to update draggability based on current turn
    window.updateChessboardDraggability = function(isPlayerTurn, gameStatus) {
        if (!window.board) return;
        
        try {
            // Create a new configuration with the updated draggable setting
            let currentPosition = window.board.position();
            let currentOrientation = window.board.orientation();
            
            // Get the original config functions if they exist
            let onDragStart = window.onDragStart || function() { return false; };
            let onDrop = window.onDrop || function() { return 'snapback'; };
            let onMouseoverSquare = window.onMouseoverSquare || function() {};
            let onMouseoutSquare = window.onMouseoutSquare || function() {};
            
            // Create a new config
            let config = {
                position: currentPosition,
                orientation: currentOrientation,
                draggable: isPlayerTurn && gameStatus === 'active',
                onDragStart: onDragStart,
                onDrop: onDrop,
                onMouseoverSquare: onMouseoverSquare,
                onMouseoutSquare: onMouseoutSquare,
                pieceTheme: '/static/img/pieces/{piece}.svg'
            };
            
            // Initialize a new board with the updated config
            window.board = Chessboard('chessboard', config);
            
            // Apply the alignment fix after updating
            setTimeout(fixChessboardAlignment, 100);
        } catch (e) {
            console.error('Error updating chessboard draggability:', e);
        }
    };
}); 