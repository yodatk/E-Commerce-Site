import React, {Component} from "react";
import {MDBBtn, MDBIcon, MDBNavLink} from "mdbreact";
import PropTypes from "prop-types";
import axios from "axios";
import {OK} from "http-status-codes";

export class ShoppingCartPage extends Component {
    state = {
        index: this.props.index,
        product_name: this.props.product_name,
        store_name: this.props.store_name,
        quantity: this.props.quantity,
        total_price: this.props.total_price,
    };

    delete = (e) => {
        this.props.deleteItem(this.state.index)
    }
    update = () => {
        this.props.updateItem(this.state.product_name, this.state.store_name, this.state.quantity, this)
        this.setState(this.state)

    }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value}, this.update);
    }

    decrease = (e) => {
        if (this.state.quantity > 1) {
            this.setState({quantity: this.state.quantity - 1}, this.update);
        }
    }

    increase = (e) => {
        this.setState({quantity: this.state.quantity + 1}, this.update);
    }


    render() {
        return (
            <tr>
                <td><MDBNavLink
                    to={`/view_product/${this.state.product_name}/${this.state.store_name}`}>{this.state.product_name}</MDBNavLink>
                </td>
                <td><MDBNavLink
                    to={`/store_page/${this.state.store_name}`}>{this.state.store_name}</MDBNavLink>
                </td>

                <td>
                    <div className="def-number-input number-input">
                        <button onClick={this.decrease} className="minus">-</button>
                        <input onChange={this.onChange} className="quantity" name="quantity"
                               value={this.state.quantity}
                               type="number"/>
                        <button onClick={this.increase} className="plus">+</button>
                    </div>
                </td>
                <td>{`${this.state.total_price}$`}</td>
                <td><MDBBtn onClick={this.delete} color="danger"><MDBIcon icon="trash"/></MDBBtn>
                </td>

            </tr>
        );
    }
}

// PropTypes
ShoppingCartPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
    product_name: PropTypes.string.isRequired,
    store_name: PropTypes.string.isRequired,
    quantity: PropTypes.number.isRequired,
    total_price: PropTypes.number.isRequired,
    refreshItems: PropTypes.func.isRequired,
    deleteItem: PropTypes.func.isRequired,
    updateItem: PropTypes.func.isRequired,
    index: PropTypes.number.isRequired,
};


export default ShoppingCartPage;