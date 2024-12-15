from policy import Policy
import numpy as np


class Policy2210xxx(Policy):
    def __init__(self,  policy_id=1):
        # Student code here
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        
        self.policy_id = policy_id
        self.patterns = []
        self.branch_stack = [] # Stack to store the branch information
        self.best_solution = None # Store the best solution found so far
        self.best_solution_score = None # Store the score of the best solution found so far
        
    def get_action(self, observation, info):
        products = observation["products"]
        stocks = observation["stocks"]
        
        if self.policy_id == 1:
            return self._policy_1_logic(products, stocks)
        elif self.policy_id == 2:
            return self._policy_2_logic(products, stocks)

    #Policy 1 is a column generation algorithm that solves the master problem to find the best placement
    def _policy_1_logic(self, products, stocks):
        # Step 1: Initialize patterns if empty
        if not self.patterns:
            self._initialize_patterns(stocks)

        # Step 2: Solve the master problem to find the best placement
        for prod in products:
            if prod["quantity"] > 0:
                action = self._solve_master_problem(prod, stocks)
                if action["stock_idx"] != -1:
                    return action

        # Step 3: If no valid placement is found, use branching
        if self.branch_stack:
            return self._branch()

        # Step 4: Generate a new pattern if no branching is possible
        for prod in products:
            if prod["quantity"] > 0:
                new_action = self._generate_column(prod, stocks)
                if new_action:
                    return new_action

        # Nếu không tìm được giải pháp
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

    def _initialize_patterns(self, stocks):
        """Khởi tạo các patterns cơ bản dựa trên kho."""
        for stock_idx, stock in enumerate(stocks):
            self.patterns.append({
                "stock_idx": stock_idx,
                "pos": [],  # Chưa đặt sản phẩm nào
            })

    def _solve_master_problem(self, prod, stocks):
        """Giải bài toán mẹ bằng cách kiểm tra các patterns hiện tại."""
        prod_size = prod["size"]
        prod_w, prod_h = prod_size

        # Duyệt qua các patterns hiện tại
        for pattern in self.patterns:
            stock_idx = pattern["stock_idx"]
            stock = stocks[stock_idx]
            stock_w, stock_h = self._get_stock_size_(stock)

            if stock_w >= prod_w and stock_h >= prod_h:
                position = self._find_position_in_pattern(pattern, stock, prod_size)
                if position:
                    posX, posY = position
                    return {"stock_idx": stock_idx, "size": prod_size, "position": (posX, posY)}

        # Nếu không tìm thấy patterns phù hợp, trả về action mặc định
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

    def _find_position_in_pattern(self, pattern, stock, prod_size):
        """Tìm vị trí phù hợp trong pattern hiện tại."""
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size

        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    return (x, y)
        return None

    def _generate_column(self, prod, stocks):
        """Sinh cột mới dựa trên sản phẩm và kho hiện tại."""
        prod_size = prod["size"]
        prod_w, prod_h = prod_size
        best_pattern = None
        best_waste = float("inf")

        for stock_idx, stock in enumerate(stocks):
            stock_w, stock_h = self._get_stock_size_(stock)

            if stock_w >= prod_w and stock_h >= prod_h:
                position = self._find_position_in_stock(stock, prod_size)
                if position:
                    # Tính waste của pattern
                    waste = (stock_w * stock_h) - (prod_w * prod_h)
                    if waste < best_waste:
                        best_waste = waste
                        best_pattern = {
                            "stock_idx": stock_idx,
                            "size": prod_size,
                            "position": position
                        }

        return best_pattern

    def _find_position_in_stock(self, stock, prod_size):
        """Tìm vị trí trong kho để đặt sản phẩm."""
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size

        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    return (x, y)
        return None

    def _branch(self):
        """Phân nhánh dựa trên các patterns hiện tại."""
        if not self.branch_stack:
            return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

        # Lấy nhánh đầu tiên từ ngăn xếp
        branch = self.branch_stack.pop()
        return branch

    def _create_branch(self, pattern):
        """Tạo nhánh mới dựa trên pattern."""
        return {
            "stock_idx": pattern["stock_idx"],
            "size": [1, 1],  # Ví dụ: nhánh mới với kích thước nhỏ hơn
            "position": (0, 0)
        }
    
    def _policy_2_logic(self, products, stocks):
         #Step 1: Initialize patterns if empty
        if not self.patterns:
             self._initialize_patterns2(stocks)
        #Step 2: Solve the master problem to find the best placement
        for prod in products:
            if prod["quantity"] > 0:
                action = self._solve_master_problem2(prod, stocks)
                if (action["stock_idx"] != -1):
                    return action
        #Step 3: If no valid placement is found, return a default action
        for prod in products:
            if prod["quantity"] > 0:
                new_action = self._generate_new_pattern2(prod, stocks)
                if(new_action["stock_idx"] != -1):
                    return new_action
        # If no valid placement is found, return a default action
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
    
    def _initialize_patterns2(self, stocks):
        """Initialize basic patterns using the current stocks."""
        for stock_idx, stocks in enumerate(stocks):
            self.patterns.append({
                "stock_idx": stock_idx,
                "pos": [],  # No products placed initially
            })
            
    def _solve_master_problem2(self, prod, stocks):
        # Solve the master problem to find the best placement
        prod_size = prod["size"]
        prod_w, prod_h = prod_size
        
        # Identify the largest valid stock by area and attempt placement
        for pattern in self.patterns:
            stock_idx = pattern["stock_idx"]
            stock = stocks[stock_idx]
            stock_w, stock_h = self._get_stock_size_(stock)
            
            if stock_w >= prod_w and stock_h >= prod_h:
                # Try to place the product in the stock with the least wasted space
                position = self._find_position_in_pattern2(pattern, stock, prod_size)
                if position:
                    posX, posY = position
                    return {"stock_idx": stock_idx, "size": prod_size, "position": (posX, posY)}
        
        # If no valid placement is found, return a default action
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
    
    def _find_position_in_pattern2(self, pattern, stock, prod_size):
        # Find the best position to place the product in the stock 
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size
        
        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    return (x, y)
        return None
    
    def _generate_new_pattern2(self, prod, stocks):
        # Generate a new pattern if no valid placement is found
        prod_size = prod["size"]
        prod_w, prod_h = prod_size
        
        # Identify the largest valid stock by area and attempt placement
        for stock_idx, stock in enumerate(stocks):
            stock_w, stock_h = self._get_stock_size_(stock)
            
            if stock_w >= prod_w and stock_h >= prod_h:
                #add a new pattern with the product placed at (0, 0) as the default position
                new_pattern = {
                    "stock_idx": stock_idx, "size": prod_size, "position": (0, 0)}
                
                self.patterns.append(new_pattern)
                return {"stock_idx": stock_idx, "size": prod_size, "position": (0, 0)}
        # If no valid placement is found, return a default action
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
    