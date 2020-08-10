import React, {Component} from "react";
import {
    MDBBtn, MDBBtnGroup,
    MDBCol,
    MDBContainer,
    MDBIcon,
    MDBInput,
    MDBNavbarBrand, MDBNavItem, MDBNavLink,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead, MDBTooltip
} from "mdbreact";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import {Link, Redirect} from "react-router-dom";
import PropTypes from "prop-types";
import {OK} from "http-status-codes";
import ShoppingCartItem from "../ShoppingCartItem";

export class ShoppingCartPage extends Component {
    state = {
        total_price: 0,
        all_items: [],
        redirectAddress: null,
        update_table: <div/>,
        item_collection: [],
        updated_item: <React.Fragment/>
    };


    decrease = (e, i) => {
        e.preventDefault()
        if (this.state.all_items[i].quantity > 1) {
            let new_items = this.state.all_items
            new_items[i]["quantity"] = new_items[i]["quantity"] - 1
            this.setState({all_items: new_items, updated_index: i}, this.updateItem);
        }
    }

    increase = (e, i) => {
        e.preventDefault()
        let new_items = this.state.all_items
        new_items[i]["quantity"] = new_items[i]["quantity"] + 1
        this.setState({all_items: new_items}, this.updateItem);
    }

    deleteItem = (i) => {
        let product_name = this.state.all_items[i]["product_name"]
        let store_name = this.state.all_items[i]["store_name"];
        axios.delete(
            `/delete_item_from_shopping_cart/${this.props.getUserId()}/${product_name}/${store_name}`
        ).then((res) => {
                console.log(res)
                if (res.status === OK) {
                    let updated_table = <div/>
                    this.setState({updated_table: updated_table}, this.refreshItems)
                }
            }
        ).catch(error => {
            console.log(error.request['error'])
        })
        this.forceUpdate();
    }


    updateItem = (product_name, store_name, quantity, to_update) => {
        axios.put(
            `/update_item_from_shopping_cart/${this.props.getUserId()}/${product_name}/${store_name}/${quantity}`
        ).then(
            (res) => {
                if (res.status === OK) {
                    let new_product = res.data;
                    console.log(new_product)

                    to_update.setState(new_product['updated'], () => {
                        this.refreshItems();
                        console.log(to_update.state)
                    })
                }

            }
        ).catch(error => {
            console.log(error.request)
        })
        //this.setState({update_table: this.state.update_table},this.forceUpdate)
        this.forceUpdate();
    }

    refreshItems = () => {
        axios.get(
            "/fetch_shopping_cart_by_user/" + this.props.getUserId())
            .then((res) => {
                if (res.status === OK) {
                    console.log(res.data);
                    let data = res.data.data;
                    let total_price = data["total_price"];
                    let baskets = data["baskets"];
                    let all_items = [];
                    if (baskets.length > 0) {
                        baskets = baskets.map(bas => bas["basket"]);
                        baskets = baskets.reduce((acc, curr) => acc.concat(curr));
                        all_items = baskets.map((item) => {
                            return {
                                total_price: item["total_price"],
                                product_name: item["product"]["name"],
                                store_name: item["product"]["store_name"],
                                quantity: item["quantity"]
                            }
                        })
                    }
                    this.setState({
                        total_price: total_price,
                        all_items: all_items
                    }, this.refreshTable)
                    if (this.props.getUserId() === -1) {
                        this.props.updateParent(res)
                    }
                } else {
                    // todo handle error
                    console.log(res)
                }
            }).catch(error => {
            console.log(error)
        });
    }

    refreshTable = () => {
        this.setState({update_table: this.renderResults()})
    }

    componentDidMount() {
        this.refreshItems(() => {
        });
    }


    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
        this.refreshItems();
    }


    renderResults = () => {
        if (this.state.all_items.length === 0) {
            return (
                <MDBContainer>
                    <MDBRow
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}>
                        <p onChange={this.onChange} className="h3 text-center mb-4">Your Cart is empty</p>
                    </MDBRow>
                </MDBContainer>

            );
        } else {
            return <MDBContainer>
                <MDBTable>
                    <MDBTableHead color="default-color" textWhite>
                        <tr>
                            <th>Product name</th>
                            <th>Store name</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th></th>
                        </tr>
                    </MDBTableHead>
                    <MDBTableBody>
                        {this.state.all_items.map((product, i) => {
                                return <ShoppingCartItem isLoggedIn={this.props.isLoggedIn}
                                                         isAdmin={this.props.isAdmin}
                                                         updateParent={this.props.updateParent}
                                                         getUserId={this.props.getUserId}
                                                         product_name={product.product_name}
                                                         store_name={product.store_name}
                                                         quantity={product.quantity}
                                                         total_price={product.total_price}
                                                         index={i}
                                                         key={`${product.product_name}@${product.store_name}`}
                                                         refreshItems={this.refreshItems}
                                                         deleteItem={this.deleteItem}
                                                         updateItem={this.updateItem}
                                />

                            }
                        )
                        }

                    </MDBTableBody>
                </MDBTable>
            </MDBContainer>
        }

    }


    render() {
        if (this.state.redirectAddress != null) {
            return <Redirect to={this.state.redirectAddress}/>
        }
         let purchase_btn = null;
        if (this.state.all_items.length !== 0) {
            purchase_btn = <MDBBtn gradient="peach"><Link style={{'color': 'white'}} to={`/purchase_items`}>Purchase</Link></MDBBtn>;
        }
        return (
            <React.Fragment>
                <MDBContainer style={{padding: "10px"}}>
                    <MDBRow
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}>
                        <p onChange={this.onChange} className="h2 text-center mb-4">Shopping Cart</p>
                    </MDBRow>
                    <MDBRow value={this.state.update_table} name="update_table">
                        {this.state.update_table}
                    </MDBRow>

                    <MDBRow style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}>
                        <h3>{`Total Price: ${this.state.total_price}$`}</h3>
                    </MDBRow>
                    <MDBRow style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}>
                        {purchase_btn}
                    </MDBRow>
                </MDBContainer>
            </React.Fragment>
        );
    }
}

// PropTypes
ShoppingCartPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
};

export default ShoppingCartPage;